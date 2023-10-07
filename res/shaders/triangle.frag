#version 450

layout(location = 0) uniform sampler2D tex;

layout(binding = 0, std140) uniform Block{
    mat4 model;
    int eid;
};

struct Light{
    float diffuse[3];
    float ambient[3];
    float position[3];
};
layout(std430, binding = 1) buffer Lights{
    Light lights[];
};

in vec2 uv_coords;
in vec3 frag_normal;
in vec3 frag_pos;

out vec4 out_color;
out int out_entity;

void main(){
    vec4 tex_color = texture(tex, uv_coords);
    out_color = vec4(0.0,0.0,0.0,0.0);
    for(int i=0; i<4; i++){
        vec3 l_pos = vec3(lights[i].position[0],lights[i].position[1],lights[i].position[2]);
        float light_angle = dot(frag_normal, normalize(l_pos-frag_pos));
        light_angle = clamp(light_angle,0,1);
        vec3 light_color = vec3(
            tex_color.x*lights[i].ambient[0] + lights[i].diffuse[0]*light_angle,
            tex_color.y*lights[i].ambient[1] + lights[i].diffuse[1]*light_angle,
            tex_color.z*lights[i].ambient[2] + lights[i].diffuse[2]*light_angle
        );
        out_color += vec4(light_color,0.0);
    }
    out_color.w += tex_color.w;
    out_entity = eid;
}