#version 420

uniform mat4 projection, modelview;

in vec2 pos;
in vec2 uv;

out vec2 uv_coords;

void main(){
    vec4 vpos = vec4(pos, 0, 1)
    uv_coords = uv;
    gl_Position = projection * modelview * vpos;
}