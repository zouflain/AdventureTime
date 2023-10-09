#version 450

layout(location = 0) uniform sampler2D tex;

layout(binding = 0, std140) uniform Block{
    mat4 model;
    int eid;
};

layout(binding = 2, std140) uniform Camera{
    mat4 projection;
    mat4 view;
};

struct Vert{
    float pos[3], normal[3];
    uint indices[4];
    float weights[4];
    vec2 uvs;
    vec4 color;
};
layout(binding = 3, std430) buffer Verts{
    Vert v_data[];
};

struct RenderBone{
    float rotation[9];
    float bind_pos[3];
    float translation[3];
};
layout(std430, binding = 4) buffer Bones{
    RenderBone bones[];
};

out vec2 uv_coords;
out vec3 frag_normal;
out vec3 frag_pos;

void main(){
    uv_coords = v_data[gl_VertexID].uvs;
    vec3 v_bind = vec3(
        v_data[gl_VertexID].pos[0],
        v_data[gl_VertexID].pos[1],
        v_data[gl_VertexID].pos[2]
    );
    vec3 v_bind_norm = vec3(
        v_data[gl_VertexID].normal[0],
        v_data[gl_VertexID].normal[1],
        v_data[gl_VertexID].normal[2]
    );
    vec3 v_pos = vec3(0);
    vec3 v_norm = vec3(0);
    for(int i=0; i<4; i++){
        uint index = v_data[gl_VertexID].indices[i];
        float weight = v_data[gl_VertexID].weights[i];
        vec3 b_bind = vec3(
                bones[index].bind_pos[0],
                bones[index].bind_pos[1],
                bones[index].bind_pos[2]
        );
        vec3 offset = v_bind; - b_bind;
        vec3 b_pos = vec3(
                bones[index].translation[0],
                bones[index].translation[1],
                bones[index].translation[2]
        );
        mat3 m_rotation;
        for(int j=0;j<9;j++){
            m_rotation[j/3][j%3] = bones[index].rotation[j];
        }
        v_pos += (b_pos+(offset*m_rotation))*weight;
        v_norm += m_rotation*v_bind_norm*weight;
    }
    /*
    /////////////////////
    vec3 normal = vec3(
        v_data[gl_VertexID].normal[0],
        v_data[gl_VertexID].normal[1],
        v_data[gl_VertexID].normal[2]
    );
    frag_normal = normal*mat3(model);
    frag_pos = (vec4(v_bind,1) * model).xyz;
    gl_Position = vec4(v_bind,1) * model * view * projection;
    ///////////////////////
    */

    frag_normal = v_norm*mat3(model);
    frag_pos = (vec4(v_pos,1) * model).xyz;
    gl_Position = vec4(v_pos,1) * model * view * projection;
}