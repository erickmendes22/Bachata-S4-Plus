// SPDX-License-Identifier: GPL-2.0-or-later
// Bachata S4+ -> unmodified game-generic shadPS4 HLE / linker / FEX guest backend.
// This file is linked into the full shadPS4 core, NEVER into libbbgpu/libmain.
#include <android/native_window_jni.h>
#include <android/log.h>
#include <jni.h>
#include <atomic>
#include <cerrno>
#include <cstdlib>
#include <mutex>
#include <string>
#include <utility>
#include <vector>

#include "android_surface.h"

namespace BachataAndroid {
std::atomic<ANativeWindow*> surface{nullptr};
std::atomic<bool> stop_requested{false};
}

// src/main.cpp is patched to rename main, preserving the whole general-purpose
// shadPS4 initialization/loader path instead of routing through BBPROBE5.
int BachataCoreMain(int argc, char* argv[]);

namespace {
constexpr const char* kTag = "BachataBionicCore";
std::mutex run_mutex;

void Fail(JNIEnv* env, const char* message) {
    if (env->ExceptionCheck()) return;
    jclass klass = env->FindClass("java/lang/IllegalStateException");
    if (klass) {
        env->ThrowNew(klass, message);
        env->DeleteLocalRef(klass);
    }
}

bool ReadArray(JNIEnv* env, jobjectArray array, std::vector<std::string>& out) {
    if (!array) return true;
    const jsize n = env->GetArrayLength(array);
    if (env->ExceptionCheck()) return false;
    for (jsize i = 0; i < n; ++i) {
        auto item = static_cast<jstring>(env->GetObjectArrayElement(array, i));
        if (!item || env->ExceptionCheck()) {
            if (item) env->DeleteLocalRef(item);
            return false;
        }
        const char* utf = env->GetStringUTFChars(item, nullptr);
        if (!utf) {
            env->DeleteLocalRef(item);
            return false;
        }
        out.emplace_back(utf);
        env->ReleaseStringUTFChars(item, utf);
        env->DeleteLocalRef(item);
    }
    return true;
}

void ApplyEnvironment(const std::vector<std::string>& envp) {
    for (const auto& entry : envp) {
        const auto equal = entry.find('=');
        if (equal == std::string::npos || equal == 0) continue;
        const std::string name = entry.substr(0, equal);
        if (name.find('=') != std::string::npos) continue;
        if (setenv(name.c_str(), entry.c_str() + equal + 1, 1) != 0)
            __android_log_print(ANDROID_LOG_WARN, kTag, "setenv %s: errno=%d",
                                name.c_str(), errno);
    }
}
}  // namespace

extern "C" JNIEXPORT jint JNICALL
Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_run(
    JNIEnv* env, jobject, jobject java_surface, jboolean,
    jobjectArray java_argv, jobjectArray java_env, jstring, jint) {
    std::unique_lock<std::mutex> lock(run_mutex, std::try_to_lock);
    if (!lock.owns_lock()) {
        Fail(env, "Bachata Bionic: emulator is already running");
        return -1;
    }
    if (!java_surface) {
        Fail(env, "Bachata Bionic: missing Android Surface");
        return -1;
    }
    ANativeWindow* window = ANativeWindow_fromSurface(env, java_surface);
    if (!window) {
        Fail(env, "Bachata Bionic: invalid Android Surface");
        return -1;
    }
    std::vector<std::string> args, envp;
    if (!ReadArray(env, java_argv, args) || !ReadArray(env, java_env, envp)) {
        ANativeWindow_release(window);
        return -1;
    }
    // The original Bachata bridge passes process arguments; keep them unchanged,
    // except for an argv[0] when the array begins with an option.
    if (args.empty() || (!args[0].empty() && args[0][0] == '-'))
        args.insert(args.begin(), "bachata-bionic");
    std::vector<char*> argv;
    argv.reserve(args.size() + 1);
    for (auto& arg : args) argv.push_back(arg.data());
    argv.push_back(nullptr);
    ApplyEnvironment(envp);
    BachataAndroid::stop_requested.store(false, std::memory_order_release);
    BachataAndroid::surface.store(window, std::memory_order_release);
    __android_log_print(ANDROID_LOG_INFO, kTag, "native generic shadPS4 launch");
    // The general core must return from its normal emulator loop on Android;
    // do not call the port's game-specific BBPROBE5 entry.
    const int result = BachataCoreMain(static_cast<int>(args.size()), argv.data());
    BachataAndroid::surface.store(nullptr, std::memory_order_release);
    ANativeWindow_release(window);
    BachataAndroid::stop_requested.store(false, std::memory_order_release);
    return result;
}

extern "C" JNIEXPORT void JNICALL
Java_com_bachatas4_android_runtime_process_NativeRuntimeBridge_stop(JNIEnv*, jobject) {
    BachataAndroid::stop_requested.store(true, std::memory_order_release);
}

extern "C" JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM*, void*) {
    return JNI_VERSION_1_6;
}
