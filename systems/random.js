export const clamp = (x, min, max) => Math.max(min, Math.min(max, x))
export const randInt = (a, b) => Math.floor(a + Math.random() * (b - a + 1))
export const normal = (mean, std) => {
  let u=0, v=0
  while(!u) u=Math.random()
  while(!v) v=Math.random()
  const z = Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)
  return mean + z*std
}