#version 450
const vec2 positions[3]=vec2[3](vec2(-1,-1),vec2(-.8,-1),vec2(-1,-.8));
void main(){gl_Position=vec4(positions[gl_VertexIndex],0,1);}
