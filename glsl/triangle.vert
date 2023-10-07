#version 420

uniform mat4 projection, model, view;

in vec3 pos;
in vec3 normal;
in uint bone_indexes[5];
in float bone_weights[5]
in vec2 tex_coords;

out vec2 uv_coords;

void main(){
    uv_coords = tex_coords;
    gl_Position = projection * view * model * pos;
}