#version 420

uniform mat4 projection, model, view;
uniform sampler2D tex;

//Lights!
uniform vec3 diffuse[4];
uniform vec3 ambient[4];
uniform vec3 position[4];

layout(location = 0) in vec3 pos;
layout(location = 1) in vec3 normal;
layout(location = 2) in uvec4 bone_indexes;
layout(location = 3) in uvec4 bone_weights;
layout(location = 4) in vec2 tex_coords;

out vec2 uv_coords;
out vec3 frag_normal;
out vec3 frag_pos;

void main(){
    uv_coords = tex_coords;
    frag_normal = normal;
    //frag_pos = (vec4(pos,1) * model).xyz;
    gl_Position = vec4(pos,1) * model * view * projection;
}