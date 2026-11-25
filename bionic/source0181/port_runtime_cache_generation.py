"""Keep persistent cache directories tied to the final compiled shader ABI."""
from pathlib import Path
import re


def apply(root):
    base = Path(root) / "src/video_core/renderer_vulkan"
    serialization = (base / "vk_pipeline_serialization.cpp").read_text()
    names = ("ShaderMetaVersion", "ShaderBinaryVersion", "PipelineKeyVersion")
    versions = []
    for name in names:
        matches = re.findall(rf"{name} = (\d+)u;", serialization)
        if len(matches) != 1:
            raise RuntimeError(f"Final cache ABI missing or ambiguous: {name}")
        versions.append(matches[0])
    version = "-".join(versions)
    cache = base / "vk_pipeline_cache.cpp"
    text, count = re.subn(r"cache-bionic-0181-\d+-\d+-\d+",
                          "cache-bionic-0181-" + version, cache.read_text())
    if count != 1:
        raise RuntimeError("Persistent shader cache namespace source drift")
    cache.write_text(text)
    return {"persistentShaderAbi": version, "previousCaches": "retained but never loaded by this ABI"}
