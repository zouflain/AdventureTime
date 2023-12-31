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
    float bind_pos[3];
    float translation[3];
    float quat[4];
};
layout(std430, binding = 4) buffer Bones{
    RenderBone bones[];
};

layout(std430, binding= 5) buffer MeshData{
    int parent_index;
    float mesh_pos[3];
    float mesh_quat[4];
};

out vec2 uv_coords;
out vec3 frag_normal;
out vec3 frag_pos;

vec4 qcross(vec4 qa, vec4 qb){
    return vec4(
        qb.w*qa.x + qb.x*qa.w - qb.y*qa.z + qb.z*qa.y,
        qb.w*qa.y + qb.x*qa.z + qb.y*qa.w - qb.z*qa.x,
        qb.w*qa.z - qb.x*qa.y + qb.y*qa.x + qb.z*qa.w,
        qb.w*qa.w - qb.x*qa.x - qb.y*qa.y - qb.z*qa.z
    );
}

vec4 qconj(vec4 qa){
    return vec4(-qa.xyz,qa.w);
}

vec4 qinv(vec4 qa){
    float s = dot(qa,qa);
    if (s > 1e-10){
        return qconj(qa)/s;
    }
    return qa;
}

vec3 qrotate(vec3 v, vec4 q){
    return qcross(qcross(q,vec4(v,0)),qinv(q)).xyz;
}

vec3 boneTransform(uint index, float weight){
    vec3 v_bind = vec3(
        v_data[gl_VertexID].pos[0],
        v_data[gl_VertexID].pos[1],
        v_data[gl_VertexID].pos[2]
    );
    vec3 b_bind = vec3(
            bones[index].bind_pos[0],
            bones[index].bind_pos[1],
            bones[index].bind_pos[2]
    );
    vec4 q_rotation = vec4(
        bones[index].quat[0],
        bones[index].quat[1],
        bones[index].quat[2],
        bones[index].quat[3]
    );
    vec3 b_pos = vec3(
            bones[index].translation[0],
            bones[index].translation[1],
            bones[index].translation[2]
    );

    //This only applies to parented items
    vec4 q_mesh = vec4(
        mesh_quat[0],
        mesh_quat[1],
        mesh_quat[2],
        mesh_quat[3]
    );
    //vec3 mpos = qrotate(vec3(mesh_pos[0],mesh_pos[1],mesh_pos[2]),q_rotation);
    vec3 mpos = vec3(mesh_pos[0],mesh_pos[1],mesh_pos[2]);

    //Output
    vec3 offset = qrotate(v_bind,q_mesh) + mpos - b_bind;
    return (b_pos+qrotate(offset,q_rotation))*weight;

}

void main(){
    uv_coords = v_data[gl_VertexID].uvs;
    vec3 v_bind_norm = vec3(
        v_data[gl_VertexID].normal[0],
        v_data[gl_VertexID].normal[1],
        v_data[gl_VertexID].normal[2]
    );
    vec3 v_pos = vec3(0);
    vec3 v_norm = vec3(0);
    if(parent_index != -1){
        v_pos += boneTransform(parent_index,1.0f);
        vec4 q_rotation = vec4(
            bones[parent_index].quat[0],
            bones[parent_index].quat[1],
            bones[parent_index].quat[2],
            bones[parent_index].quat[3]
        );

        vec4 q_mesh = vec4(
            mesh_quat[0],
            mesh_quat[1],
            mesh_quat[2],
            mesh_quat[3]
        );
        v_norm += qrotate(v_bind_norm, qcross(q_rotation,q_mesh));
    }else {
        for (int i = 0; i < 4; i++) {
            uint index = v_data[gl_VertexID].indices[i];
            float weight = v_data[gl_VertexID].weights[i];
            vec4 q_rotation = vec4(
                bones[index].quat[0],
                bones[index].quat[1],
                bones[index].quat[2],
                bones[index].quat[3]
            );
            v_norm += qrotate(v_bind_norm, q_rotation) * weight;
            v_pos += boneTransform(index, weight);
        }
    }
    frag_normal = v_norm*mat3(model);
    frag_pos = (vec4(v_pos,1) * model).xyz;
    gl_Position = vec4(v_pos,1) * model * view * projection;
}