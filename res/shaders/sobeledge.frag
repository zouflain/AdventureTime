#version 420

uniform sampler2D tex;

out vec4 out_color;

in vec2 uv_coords;
in vec3 frag_normal;
in vec3 frag_pos;

const int w = 3;
const float sobel[9] = {
    -1.0f, 0.0f, 1.0f,
    -2.0f, 0.0f, 2.0f,
    -1.0f, 0.0f, 1.0f
};

void main(){
    float sobel_x = 0;
    float sobel_y = 0;
    for(int y=0;y<3;y++){
        for(int x=0;x<3;x++){
            vec4 source = texture(tex,uv_coords+vec2(x-1,y-1));
            sobel_x += (source*sobel[y*w+x]).x;
            sobel_y += (source*sobel[x*w+y]).x;

        }
    }
    float sobel_final = sqrt(sobel_x*sobel_x+sobel_y+sobel_y);

    out_color = vec4(sobel_final);
}