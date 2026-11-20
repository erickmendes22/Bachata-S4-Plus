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

namespace {
constexpr const char* kTag = "BachataBionic";
constexpr const char* kRunSymbol =
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run";
constexpr const char* kStopSymbol =
    "Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop";
// Do not load libmain.so from the Uncharted port here: it uses SDLActivity
// and a BBPROBE5 guest image, not this exact JNI+ANativeWindow contract.
constexpr const char* kCore = "libbachata_bionic_core.so";
constexpr const char* kLegacy = "libbachata_release_legacy.so";

using Run = jint (*)(JNIEnv*, jobject, jobject, jboolean,
                     jobjectArray, jobjectArray, jstring, jint);
using Stop = void (*)(JNIEnv*, jobject);
using OnLoad = jint (*)(JavaVM*, void*);

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

bool try_engine(JNIEnv* env, const char* name) {
    void* h = dlopen(name, RTLD_NOW | RTLD_LOCAL);
    if (!h) {
        __android_log_print(ANDROID_LOG_INFO, kTag, "%s absent: %s", name, dlerror());
        return false;
    }
    auto run = reinterpret_cast<Run>(dlsym(h, kRunSymbol));
    auto stop = reinterpret_cast<Stop>(dlsym(h, kStopSymbol));
    if (!run || !stop) {
        // A port's SDL_main cannot be invoked by NativeRuntimeBridge.run.
        __android_log_print(ANDROID_LOG_WARN, kTag,
                            "%s lacks exact Bachata JNI ABI; skipping", name);
        dlclose(h);
        return false;
    }
    auto onload = reinterpret_cast<OnLoad>(dlsym(h, "JNI_OnLoad"));
    if (onload) {
        JavaVM* vm = nullptr;
        if (env->GetJavaVM(&vm) != JNI_OK ||
            onload(vm, nullptr) == JNI_ERR || env->ExceptionCheck()) {
            __android_log_print(ANDROID_LOG_ERROR, kTag,
                                "%s failed JNI_OnLoad", name);
            dlclose(h);
            return false;
        }
    }
    engine = {h, run, stop, name};
    __android_log_print(ANDROID_LOG_INFO, kTag, "using Bionic engine: %s", name);
    return true;
}

Engine choose_engine(JNIEnv* env) {
    std::lock_guard<std::mutex> guard(engine_lock);
    if (!engine.run) {
        // Native full shadPS4/FEX implementation takes priority.
        // Legacy v0.2.5 is a known-good Bionic compatibility baseline.
        if (!try_engine(env, kCore) && !try_engine(env, kLegacy))
            return {};
    }
    return engine;
}
} // namespace

extern "C" JNIEXPORT jint JNICALL
Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run(
    JNIEnv* env, jobject receiver, jobject surface, jboolean option,
    jobjectArray arguments, jobjectArray environment, jstring root, jint flags) {
    const Engine selected = choose_engine(env);
    if (!selected.run) {
        throw_java(env,
            "No compatible native Bionic core. libmain.so is not a drop-in "
            "replacement for Bachata NativeRuntimeBridge.run; the legacy "
            "Bionic runtime or a full native core must be bundled.");
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

extern "C" JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM*, void*) {
    return JNI_VERSION_1_6;
}
