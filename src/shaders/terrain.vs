varying vec2 uv;

void main()
{
	vec4 position = gl_Vertex;
	uv = position.xy / 500.0;
	uv = uv * 0.5 + 0.5;
	gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * position;
}