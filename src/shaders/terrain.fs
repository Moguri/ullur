varying vec2 uv;

uniform sampler2D stencil_map;
uniform sampler2D diffuse_r;
uniform sampler2D diffuse_g;
uniform sampler2D diffuse_b;
uniform sampler2D diffuse_a;

void main()
{
	vec4 m = texture2D(stencil_map, uv);
	m /= dot(m, vec4(1.0));
	
	vec2 tile = uv * 16.0;
	
	vec3 r = texture2D(diffuse_r, tile).rgb * m.x;
	vec3 g = texture2D(diffuse_g, tile).rgb * m.y;
	vec3 b = texture2D(diffuse_b, tile).rgb * m.z;
	vec3 a = texture2D(diffuse_a, tile).rgb * m.w;
	
	vec3 color = r + g + b + a;
	
	gl_FragColor.xyz = color;
}