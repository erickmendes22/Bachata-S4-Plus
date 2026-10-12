// SPDX-License-Identifier: GPL-2.0-or-later
// Included at the bottom of temporal_generic.cpp within its anonymous namespace.
// Uses Bloodborne-Android's camera_motion.comp and 108-byte motion push constants.
bool build_camera_compute() {
    VkDescriptorSetLayoutBinding bindings[2]{};
    bindings[0].binding=0;bindings[0].descriptorCount=1;
    bindings[0].descriptorType=VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE;
    bindings[0].stageFlags=VK_SHADER_STAGE_COMPUTE_BIT;
    bindings[1].binding=1;bindings[1].descriptorCount=1;
    bindings[1].descriptorType=VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
    bindings[1].stageFlags=VK_SHADER_STAGE_COMPUTE_BIT;
    VkDescriptorSetLayoutCreateInfo sl{VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO};
    sl.bindingCount=2;sl.pBindings=bindings;
    if(!result(vkCreateDescriptorSetLayout(device,&sl,nullptr,&camera_desc_layout),
               "guest camera descriptor layout"))return false;
    VkPushConstantRange range{VK_SHADER_STAGE_COMPUTE_BIT,0,
        uint32_t(sizeof(Bachata::Fsr31::MotionPush))};
    VkPipelineLayoutCreateInfo pl{VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    pl.setLayoutCount=1;pl.pSetLayouts=&camera_desc_layout;
    pl.pushConstantRangeCount=1;pl.pPushConstantRanges=&range;
    if(!result(vkCreatePipelineLayout(device,&pl,nullptr,&camera_pipeline_layout),
               "camera pipeline layout"))return false;
    VkShaderModule shader{};
    VkShaderModuleCreateInfo sm{VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO};
    sm.codeSize=sizeof(BS4_FSR31_CAMERA_SPV);
    sm.pCode=BS4_FSR31_CAMERA_SPV;
    if(!result(vkCreateShaderModule(device,&sm,nullptr,&shader),
               "port camera motion shader"))return false;
    VkComputePipelineCreateInfo ci{VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO};
    ci.stage={VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO};
    ci.stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;
    ci.stage.module=shader;ci.stage.pName="main";ci.layout=camera_pipeline_layout;
    const auto status=vkCreateComputePipelines(device,VK_NULL_HANDLE,1,&ci,nullptr,&camera_pipeline);
    vkDestroyShaderModule(device,shader,nullptr);
    if(!result(status,"camera motion pipeline"))return false;
    VkDescriptorPoolSize sizes[2]={{VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE,4},
                                   {VK_DESCRIPTOR_TYPE_STORAGE_IMAGE,4}};
    VkDescriptorPoolCreateInfo dp{VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO};
    dp.maxSets=4;dp.poolSizeCount=2;dp.pPoolSizes=sizes;
    return result(vkCreateDescriptorPool(device,&dp,nullptr,&camera_pool),
                  "camera descriptor pool");
}
void camera_flow(VkCommandBuffer cb,const Frame& frame,VkExtent2D size,
                 const Bachata::Fsr31::MotionPush& push) {
    VkDescriptorImageInfo images[2]{};
    images[0].imageView=frame.depth.view;
    images[0].imageLayout=VK_IMAGE_LAYOUT_SHADER_READ_ONLY_OPTIMAL;
    images[1].imageView=frame.motion.view;
    images[1].imageLayout=VK_IMAGE_LAYOUT_GENERAL;
    VkWriteDescriptorSet writes[2]{};
    for(uint32_t i=0;i<2;i++){
        writes[i]={VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET};
        writes[i].dstSet=frame.cameraDescriptor;
        writes[i].dstBinding=i;writes[i].descriptorCount=1;
        writes[i].descriptorType=i==0?VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE:
                                     VK_DESCRIPTOR_TYPE_STORAGE_IMAGE;
        writes[i].pImageInfo=&images[i];
    }
    vkUpdateDescriptorSets(device,2,writes,0,nullptr);
    vkCmdBindPipeline(cb,VK_PIPELINE_BIND_POINT_COMPUTE,camera_pipeline);
    vkCmdBindDescriptorSets(cb,VK_PIPELINE_BIND_POINT_COMPUTE,
                            camera_pipeline_layout,0,1,&frame.cameraDescriptor,0,nullptr);
    vkCmdPushConstants(cb,camera_pipeline_layout,VK_SHADER_STAGE_COMPUTE_BIT,
                       0,uint32_t(sizeof(push)),&push);
    vkCmdDispatch(cb,(size.width+7)/8,(size.height+7)/8,1);
}