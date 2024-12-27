function calculatePolar() {
  const x1 = parseFloat(document.getElementById('x1').value);
  const y1 = parseFloat(document.getElementById('y1').value);
  const x2 = parseFloat(document.getElementById('x2').value);
  const y2 = parseFloat(document.getElementById('y2').value);

  // 거리를 계산합니다.
  const distance = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);

  // 방위각을 계산합니다.
  let angleRad = Math.atan2(y2 - y1, x2 - x1);

  // 라디안에서 도로 변환하고 각도를 표현합니다.
  let angleDeg = angleRad * (180 / Math.PI);
  if (angleDeg < 0) {
    angleDeg += 360;
  }

  const degrees = Math.floor(angleDeg);
  const minutes = Math.floor((angleDeg - degrees) * 60);
  const seconds = Math.floor(((angleDeg - degrees) * 60 - minutes) * 60);

  const angle = `${degrees}° ${minutes}' ${seconds}''`;

  document.getElementById('result').innerText = `방위각: ${angle}\n거리: ${distance.toFixed(2)}`;
}