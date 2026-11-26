// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include <algorithm>
#include <cstdint>
#include <limits>

namespace BachataGpu {

struct IndirectIndexRequest {
    uint32_t bytes{};
    // The donor leaves INDEX_BUFFER_SIZE == 0 uncapped; a stale NUM_INDICES
    // register must not become an invented limit on GPU-produced counts.
    uint32_t limit{std::numeric_limits<uint32_t>::max()};
};

constexpr IndirectIndexRequest ResolveIndirectIndices(uint32_t num_indices,
                                                       uint32_t max_index_size,
                                                       uint32_t index_size,
                                                       uint64_t mapped_bytes) {
    if (!index_size) return {0, 0};
    const uint32_t wanted = max_index_size ? max_index_size : num_indices;
    const uint64_t bytes = std::min({uint64_t(wanted) * index_size, mapped_bytes,
                                    uint64_t(std::numeric_limits<uint32_t>::max())});
    const uint32_t aligned = uint32_t(bytes - bytes % index_size);
    if (!aligned) return {0, 0};
    return {aligned, max_index_size ? aligned / index_size
                                   : std::numeric_limits<uint32_t>::max()};
}

struct IndirectRecords {
    uint32_t count{};
    uint32_t bytes{};
};

// Keep only complete records inside the mapped guest span and the buffer-cache
// API's representable byte range. A padded stride is valid. For one record the
// hardware does not consume stride, so zero is valid too.
constexpr IndirectRecords ResolveIndirectRecords(uint32_t count, uint32_t stride,
                                                   uint32_t record_bytes,
                                                   uint64_t mapped_bytes) {
    if (!count || !record_bytes || (stride & 3) ||
        (count > 1 && stride < record_bytes)) return {};
    const uint64_t available = std::min(mapped_bytes,
                                        uint64_t(std::numeric_limits<uint32_t>::max()));
    if (available < record_bytes) return {};
    if (count > 1) count = uint32_t(std::min<uint64_t>(count,
        1 + (available - record_bytes) / stride));
    return {count, uint32_t(uint64_t(count - 1) * stride + record_bytes)};
}

struct IndirectClampBatch {
    uint32_t count{};
    uint64_t source_begin{};
    uint64_t source_bytes{};
    uint64_t output_bytes{};
    uint32_t first_word{};
};

// Each output starts with one GPU-written count word, then packed five-word
// VkDrawIndexedIndirectCommand records. Split at descriptor/dispatch/draw limits
// instead of dropping valid records when a device exposes a smaller maximum.
constexpr IndirectClampBatch PlanIndirectClampBatch(uint32_t remaining, uint32_t stride,
                                                      uint64_t source_offset, uint64_t alignment,
                                                      uint64_t storage_range,
                                                      uint32_t max_dispatch_x,
                                                      uint32_t max_draw_count) {
    constexpr uint64_t RecordBytes = 5 * sizeof(uint32_t);
    if (!remaining || !alignment || !max_dispatch_x || !max_draw_count ||
        (stride & 3) || (remaining > 1 && stride < RecordBytes)) return {};
    const uint64_t begin = source_offset - source_offset % alignment;
    const uint64_t prefix = source_offset - begin;
    if ((prefix & 3) || storage_range < prefix + RecordBytes ||
        storage_range < sizeof(uint32_t) + RecordBytes) return {};
    const uint64_t source_count = stride ? 1 + (storage_range - prefix - RecordBytes) / stride : 1;
    const uint64_t destination_count = (storage_range - sizeof(uint32_t)) / RecordBytes;
    const uint32_t count = uint32_t(std::min({uint64_t(remaining), source_count,
        destination_count, uint64_t(max_dispatch_x) * 64, uint64_t(max_draw_count)}));
    if (!count) return {};
    return {count, begin, prefix + uint64_t(count - 1) * stride + RecordBytes,
            sizeof(uint32_t) + uint64_t(count) * RecordBytes, uint32_t(prefix / sizeof(uint32_t))};
}

} // namespace BachataGpu
