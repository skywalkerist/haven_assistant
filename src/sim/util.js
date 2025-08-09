// 通用工具函数
export function clamp01(x) { 
  return Math.max(0, Math.min(1, x)); 
}

export function randInt(a, b) { 
  return Math.round(a + Math.random() * (b - a)); 
}

// 等额本息年供计算
export function annuity(loan, annualRate, years) {
  const r = annualRate; 
  const n = years;
  if (r <= 0) return Math.ceil(loan / n);
  const factor = (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
  return Math.ceil(loan * factor);
}