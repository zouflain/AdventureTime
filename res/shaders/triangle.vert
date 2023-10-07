#version 450

layout(binding = 0, std140) uniform Block{
    mat4 model;
    int eid;
};

layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 normal;
layout(location = 2) in uvec4 bone_indexes;
layout(location = 3) in uvec4 bone_weights;
layout(location = 4) in vec2 tex_coords;
layout(location = 5) in vec4 vert_color;

layout(location = 6) uniform mat4 projection;
layout(location = 8) uniform mat4 view;

layout(location = 9) uniform sampler2D tex;

out vec2 uv_coords;
out vec3 frag_normal;
out vec3 frag_pos;

void main(){
    uv_coords = tex_coords;
    frag_normal = normal;
    frag_pos = (vec4(pos,1) * model).xyz;
    gl_Position = vec4(pos,1) * model * view * projection;
}