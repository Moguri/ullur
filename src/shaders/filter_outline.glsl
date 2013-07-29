uniform sampler2D bgl_RenderedTexture;
uniform sampler2D bgl_DepthTexture;
uniform vec2 bgl_TextureCoordinateOffset[9];

const float bias = 0.00025;
const int thickness = 2;

void main()
{
	vec2 uv = gl_TexCoord[0].st;
	vec3 render = texture2D(bgl_RenderedTexture, uv).rgb;
	float depth = texture2D(bgl_DepthTexture, uv).r;
	
	int edge = 0;
	float sdepth;
	vec2 offset[9] = bgl_TextureCoordinateOffset;
	
	for (int i = 1; i < thickness+1; i++) {
		sdepth = texture2D(bgl_DepthTexture, uv+offset[3]*i).r;
		edge += (sdepth > depth+bias) ? 1 : 0;
		
		sdepth = texture2D(bgl_DepthTexture, uv+offset[5]*i).r;
		edge += (sdepth > depth+bias) ? 1 : 0;
		
		sdepth = texture2D(bgl_DepthTexture, uv+offset[1]*i).r;
		edge += (sdepth > depth+bias) ? 1 : 0;
		
		sdepth = texture2D(bgl_DepthTexture, uv+offset[7]*i).r;
		edge += (sdepth > depth+bias) ? 1 : 0;
	}
	
	if (edge > 0)
		gl_FragColor = vec4(render*0.66, 1.0);
		// gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
	else
		gl_FragColor = vec4(render, 1.0);
}