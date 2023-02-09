export const clamp = (target, min, max) => {
	return Math.min(Math.max(target, min), max)
}

export const rgbLogShade=(p, c) => {
    var i=parseInt,r=Math.round,[a,b,c,d]=c.split(","),P=p<0,t=P?0:p*255**2,P=P?1+p:1-p;
    return"rgb"+(d?"a(":"(")+r((P*i(a[3]=="a"?a.slice(5):a.slice(4))**2+t)**0.5)+","+r((P*i(b)**2+t)**0.5)+","+r((P*i(c)**2+t)**0.5)+(d?","+d:")");
}

export const m32 = (a) => {
	var t = a += 0x6D2B79F5;
	t = Math.imul(t ^ t >>> 15, t | 1);
	t ^= t + Math.imul(t ^ t >>> 7, t | 61);
	return ((t ^ t >>> 14) >>> 0) / 4294967296;
}

export const cubicBezier = (t, y1, y2) => {
	return 3*t*y1*(1-t)**2 + 3*y2*(1-t)*t**2 + t**3
}

export const custom = (t) => {
	return 1.06 + (-1.06)/(1 + (8.3*t)**1.3)
}