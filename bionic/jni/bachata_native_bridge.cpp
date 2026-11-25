// Bachata S4+ -- Android Bionic JNI-ABI handoff.
// Reconstructed from the unmodified v0.2.5 release DEX and ELF exports.
// This shim does not invent a second Java API. It keeps the original
// NativeRuntimeBridge.run/stop contract while native core integration evolves.
// The original release may be supplied as libbachata_release_legacy.so for a
// compatibility fallback; no proprietary binary is stored in the source tree.
#include <jni.h>
#include <android/log.h>
#include <dlfcn.h>
#include <mutex>
#include <atomic>
#include <cstdio>
#include <unistd.h>
#include <fcntl.h>
#include <cerrno>
#include <cstring>
#include <string>
#include <vector>
#include "core_title_selector.h"

namespace {
constexpr const char* kTag = "BachataBionic";
constexpr const char* kRunSymbol =
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run";
constexpr const char* kStopSymbol =
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop";
// Do not load libmain.so from the Uncharted port here: it uses SDLActivity
// and a BBPROBE5 guest image, not this exact JNI+ANativeWindow contract.
constexpr const char* kCore = "libbachata_bionic_core.so";
constexpr const char* kSotcCore = "libbachata_sotc_core.so";

using Run = jint (*)(JNIEnv*, jobject, jobject, jboolean,
                     jobjectArray, jobjectArray, jstring, jint);
using Stop = void (*)(JNIEnv*, jobject);

struct Engine {
    void* handle = nullptr;
    Run run = nullptr;
    Stop stop = nullptr;
    const char* name = nullptr;
};
std::mutex engine_lock;
Engine engine;
std::atomic<Stop> active_stop{nullptr};

void throw_java(JNIEnv* env, const char* message) {
    jclass ex = env->FindClass("java/lang/IllegalStateException");
    if (ex) {
        env->ThrowNew(ex, message);
        env->DeleteLocalRef(ex);
    }
}

// The original NativeRuntimeBridge.run receives a working directory AND an
// output file descriptor. The JNI adapter must honor both: shadPS4 uses the
// process working directory for configuration, and the Android UI only records
// stdout/stderr that reach the supplied diagnostics descriptor.
struct ScopedServiceProcessIO {
    int previous_directory = -1;
    int previous_stdout = -1;
    int previous_stderr = -1;
    bool ok = false;

    ScopedServiceProcessIO(JNIEnv* env, jstring directory, jint output_fd) {
        // Android's isolated service may have search but not read permission
        // for its inherited current directory. O_PATH can save a cwd without
        // requiring directory read access; failure to save cwd is NOT a boot
        // failure for this dedicated runtime service process.
#ifdef O_PATH
        previous_directory = open(".", O_PATH | O_CLOEXEC);
#else
        previous_directory = open(".", O_RDONLY | O_CLOEXEC);
#endif
        if (previous_directory < 0) {
            __android_log_print(ANDROID_LOG_WARN, kTag,
                                "Cannot save inherited cwd (errno=%d); using runtime cwd",
                                errno);
        }
        if (!directory) {
            throw_java(env, "Bachata Bionic: missing working directory");
            return;
        }
        const char* path = env->GetStringUTFChars(directory, nullptr);
        if (!path) return;
        const int rc = chdir(path);
        const int error = errno;
        env->ReleaseStringUTFChars(directory, path);
        if (rc != 0) {
            __android_log_print(ANDROID_LOG_ERROR, kTag, "chdir failed: errno=%d", error);
            throw_java(env, "Bachata Bionic: cannot enter runtime working directory");
            return;
        }
        if (output_fd >= 0) {
            fflush(nullptr);
            previous_stdout = dup(STDOUT_FILENO);
            previous_stderr = dup(STDERR_FILENO);
            if (dup2(output_fd, STDOUT_FILENO) < 0 ||
                dup2(output_fd, STDERR_FILENO) < 0) {
                throw_java(env, "Bachata Bionic: cannot redirect runtime logs");
                return;
            }
            // CRITICAL: the native service owns output_fd and closes it itself.
            setvbuf(stdout, nullptr, _IONBF, 0);
            setvbuf(stderr, nullptr, _IONBF, 0);
        }
        ok = true;
    }

    ~ScopedServiceProcessIO() {
        fflush(nullptr);
        if (previous_stdout >= 0) {
            dup2(previous_stdout, STDOUT_FILENO);
            close(previous_stdout);
        }
        if (previous_stderr >= 0) {
            dup2(previous_stderr, STDERR_FILENO);
            close(previous_stderr);
        }
        if (previous_directory >= 0) {
            fchdir(previous_directory);
            close(previous_directory);
        }
    }
};

// The frontend supplies the selected Vulkan driver and guest environment
// to NativeRuntimeBridge.run(). They must be active BEFORE the core ELF is
// loaded: Bionic ELF constructors can read HOME, XDG_* and Vulkan loader
// settings during System.loadLibrary(), not only during BachataCoreMain().
bool apply_service_environment(JNIEnv* env, jobjectArray environment) {
    if (!environment) return true;
    const jsize n = env->GetArrayLength(environment);
    if (env->ExceptionCheck()) return false;
    for (jsize i = 0; i < n; ++i) {
        auto item = static_cast<jstring>(env->GetObjectArrayElement(environment, i));
        if (env->ExceptionCheck()) return false;
        if (!item) continue;
        const char* raw = env->GetStringUTFChars(item, nullptr);
        if (!raw) {
            env->DeleteLocalRef(item);
            return false;
        }
        const std::string setting(raw);
        env->ReleaseStringUTFChars(item, raw);
        env->DeleteLocalRef(item);
        const auto eq = setting.find('=');
        if (eq == std::string::npos || eq == 0) continue;
        const std::string name = setting.substr(0, eq);
        if (setenv(name.c_str(), setting.c_str() + eq + 1, 1) != 0) {
            __android_log_print(ANDROID_LOG_ERROR, kTag,
                                "Native service setenv failed: %s errno=%d",
                                name.c_str(), errno);
            throw_java(env, "Bachata Bionic: runtime environment initialization failed");
            return false;
        }
    }
    return true;
}

// Java helper is deliberately invoked AFTER cwd + environment are prepared.
// Java's System.loadLibrary registers core JNI_OnLoad in this application's
// ClassLoader. A raw dlopen alone does not do that, and manually calling
// JNI_OnLoad from our adapter would create an inconsistent SDL runtime.
bool load_core_from_service_classloader(JNIEnv* env, bool sotc) {
    jclass bridge = env->FindClass(
        "com/bachatas4/android/runtime/process/NativeRuntimeBridge");
    if (!bridge || env->ExceptionCheck()) return false;
    jmethodID init = env->GetStaticMethodID(bridge, "loadCoreAndSetupJNI", "(Z)V");
    if (!init || env->ExceptionCheck()) {
        env->DeleteLocalRef(bridge);
        return false;
    }
    env->CallStaticVoidMethod(bridge, init, static_cast<jboolean>(sotc));
    env->DeleteLocalRef(bridge);
    if (env->ExceptionCheck()) {
        __android_log_print(ANDROID_LOG_ERROR, kTag,
                            "BIONIC_CORE_JAVA_LOAD_OR_SDL_SETUP_FAILED");
        // Include the actual JNI/ELF exception in Android logcat, but do
        // not swallow it: the service must still receive the cause.
        jthrowable failure = env->ExceptionOccurred();
        env->ExceptionDescribe();  // JNI clears the pending exception.
        if (failure) {
            env->Throw(failure);
            env->DeleteLocalRef(failure);
        }
        return false;
    }
    __android_log_print(ANDROID_LOG_INFO, kTag,
                        "BIONIC_CORE_LOADED_AFTER_SERVICE_SETUP");
    return true;
}

bool try_engine(const char* name) {
    void* h = dlopen(name, RTLD_NOW | RTLD_LOCAL);
    if (!h) {
        const char* error = dlerror();
        __android_log_print(ANDROID_LOG_ERROR, kTag, "BIONIC_CORE_DLOPEN_FAILED: %s: %s", name,
                            error ? error : "unknown linker error");
        fprintf(stderr, "BIONIC_CORE_DLOPEN_FAILED: %s: %s\n", name,
                error ? error : "unknown linker error");
        fflush(stderr);
        return false;
    }
    auto run = reinterpret_cast<Run>(dlsym(h, kRunSymbol));
    auto stop = reinterpret_cast<Stop>(dlsym(h, kStopSymbol));
    if (!run || !stop) {
        // A port's SDL_main cannot be invoked by NativeRuntimeBridge.run.
        __android_log_print(ANDROID_LOG_WARN, kTag,
                            "%s lacks exact Bachata JNI ABI; skipping", name);
        fprintf(stderr, "[BachataBionic] missing JNI run/stop export: %s\n", name);
        dlclose(h);
        return false;
    }
    // Core is preloaded through Java System.loadLibrary in the actual
    // application ClassLoader, which calls JNI_OnLoad exactly once.
    // Calling JNI_OnLoad again from a raw dlopen is invalid for SDL's
    // registration and can leave duplicate or corrupted Java global refs.
    engine = {h, run, stop, name};
    __android_log_print(ANDROID_LOG_INFO, kTag, "using Bionic engine: %s", name);
    return true;
}

bool select_sotc(JNIEnv* env,jobjectArray arguments) {
    if(!arguments)return false;
    std::vector<std::string> strings;
    const auto n=env->GetArrayLength(arguments);
    strings.reserve(n);
    for(jsize i=0;i<n;++i) {
        auto item=static_cast<jstring>(env->GetObjectArrayElement(arguments,i));
        if(env->ExceptionCheck())return false;
        if(!item){strings.emplace_back();continue;}
        const char* raw=env->GetStringUTFChars(item,nullptr);
        if(!raw){env->DeleteLocalRef(item);return false;}
        strings.emplace_back(raw);
        env->ReleaseStringUTFChars(item,raw);
        env->DeleteLocalRef(item);
    }
    std::vector<std::string_view> views;
    views.reserve(strings.size());
    for(const auto& value:strings)views.emplace_back(value);
    return BachataDispatch::SotcArgs(views);
}
Engine choose_engine(JNIEnv* env,bool sotc) {
    std::lock_guard<std::mutex> guard(engine_lock);
    const char* selected=sotc?kSotcCore:kCore;
    // A service process owns exactly one FEX/SDL core for its lifetime.
    // Never load both cores, never silently fall back to the other.
    if(engine.run) {
        if(std::strcmp(engine.name,selected)!=0) {
            throw_java(env,"Bachata: restart runtime service before changing core");
            return {};
        }
        return engine;
    }
    if(!load_core_from_service_classloader(env,sotc)||!try_engine(selected))
        return {};
    std::fprintf(stderr,"BACHATA_CORE_DISPATCH profile=%s library=%s\n",
                 sotc?"SotC-color-recovery":"main",selected);
    return engine;
}
} // namespace

extern "C" JNIEXPORT jint JNICALL
Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run(
    JNIEnv* env, jobject receiver, jobject surface, jboolean option,
    jobjectArray arguments, jobjectArray environment, jstring root, jint flags) {
    // The Binder worker passes this exact JNI contract: its working directory
    // and log FD must be active BEFORE loading the native core.
    ScopedServiceProcessIO process_io(env, root, flags);
    if (!process_io.ok) return -1;
    if (!apply_service_environment(env, environment)) return -1;
    const bool sotc=select_sotc(env,arguments);
    if(env->ExceptionCheck())return -1;
    const Engine selected=choose_engine(env,sotc);
    if(!selected.run) {
        if(!env->ExceptionCheck())throw_java(env,"Bachata: selected Bionic core could not load");
        return -1;
    }
    // The service is the owner of surface, arrays, strings, and process life.
    // Forward unchanged: do not reinterpret or copy game paths/driver data.
    active_stop.store(selected.stop, std::memory_order_release);
    const jint result = selected.run(env, receiver, surface, option,
                                     arguments, environment, root, flags);
    active_stop.store(nullptr, std::memory_order_release);
    return result;
}

extern "C" JNIEXPORT void JNICALL
Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop(
    JNIEnv* env, jobject receiver) {
    auto stop = active_stop.load(std::memory_order_acquire);
    if (stop) stop(env, receiver);
}

extern "C" JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void*) {
    // Both the adapter and core export NativeRuntimeBridge.run/stop. Bind
    // these methods explicitly to this adapter, so ART's ClassLoader library
    // search order cannot bypass the required cwd, diagnostics FD and
    // native-core dispatch.
    JNIEnv* env = nullptr;
    if (!vm || vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK)
        return JNI_ERR;
    jclass bridge = env->FindClass(
        "com/bachatas4/android/runtime/process/NativeRuntimeBridge");
    if (!bridge) return JNI_ERR;
    JNINativeMethod methods[] = {
        {const_cast<char*>("run"),
         const_cast<char*>("(Landroid/view/Surface;Z[Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;I)I"),
         reinterpret_cast<void*>(Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run)},
        {const_cast<char*>("stop"), const_cast<char*>("()V"),
         reinterpret_cast<void*>(Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop)},
    };
    const jint status = env->RegisterNatives(bridge, methods, 2);
    env->DeleteLocalRef(bridge);
    if (status != JNI_OK) {
        __android_log_print(ANDROID_LOG_ERROR, kTag,
                            "BIONIC_ADAPTER_JNI_REGISTRATION_FAILED");
        return JNI_ERR;
    }
    __android_log_print(ANDROID_LOG_INFO, kTag, "BIONIC_ADAPTER_JNI_REGISTERED");
    return JNI_VERSION_1_6;
}
