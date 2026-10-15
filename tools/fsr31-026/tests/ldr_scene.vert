#version 450
layout(constant_id=0) const bool hardwareWindow=false;
layout(constant_id=1) const float hardwareWidth=16384.0;
layout(constant_id=2) const float hardwareHeight=16384.0;
layout(push_constant) uniform Push { vec4 viewport; } raw;
void main(){
    vec2 p=vec2((gl_VertexIndex<<1)&2,gl_VertexIndex&2);
    vec2 position=p*2.0-1.0;
    // Exact core025 ConvertPositionToClipSpace conversion for clip-disable.
    if(hardwareWindow)position=(position*raw.viewport.zw+raw.viewport.xy)/
                              (vec2(hardwareWidth,hardwareHeight)/2.0)-1.0;
    gl_Position=vec4(position,0.0,1.0);
}
