document.addEventListener('DOMContentLoaded', () => {
    const addPointButton = document.getElementById('addPoint');
    const calculateButton = document.getElementById('calculateBtn');
    const pointsContainer = document.getElementById('pointsContainer');
    const calculatedResultsDiv = document.getElementById('calculatedResults');

    let pointCount = 1;

    // Function to convert degrees, minutes, seconds to radians
    function dmsToRadians(degrees, minutes, seconds) {
        const totalDegrees = parseFloat(degrees) + parseFloat(minutes) / 60 + parseFloat(seconds) / 3600;
        return totalDegrees * (Math.PI / 180);
    }

    // Function to calculate new coordinates (MODIFIED: X with cos, Y with sin)
    function calculateNewCoordinate(originX, originY, bearingRadians, distance) {
        // IMPORTANT: This assumes bearing is measured from the positive X-axis (East) counter-clockwise.
        // If your bearing is North-based clockwise, you might need to adjust the input bearing itself
        // (e.g., bearingRadians = Math.PI / 2 - originalBearingRadians for North-based clockwise to math standard).
        // Based on user request, X uses cos, Y uses sin directly from the provided bearingRadians.
        const deltaX = distance * Math.cos(bearingRadians);
        const deltaY = distance * Math.sin(bearingRadians);

        const newX = originX + deltaX;
        const newY = originY + deltaY;

        return { x: newX, y: newY };
    }

    // Add another point input group
    addPointButton.addEventListener('click', () => {
        pointCount++;
        const newPointDiv = document.createElement('div');
        newPointDiv.classList.add('point-input');
        newPointDiv.innerHTML = `
            <h2>Point ${pointCount}</h2>
            <label for="bearingDeg${pointCount}">Bearing (Degrees):</label>
            <input type="number" id="bearingDeg${pointCount}" value="0" min="0" max="359">
            <label for="bearingMin${pointCount}">Minutes:</label>
            <input type="number" id="bearingMin${pointCount}" value="0" min="0" max="59">
            <label for="bearingSec${pointCount}">Seconds:</label>
            <input type="number" id="bearingSec${pointCount}" value="0" min="0" max="59">
            <label for="distance${pointCount}">Distance:</label>
            <input type="number" id="distance${pointCount}" value="0">
        `;
        pointsContainer.appendChild(newPointDiv);
    });

    // Calculate button event listener
    calculateButton.addEventListener('click', () => {
        calculatedResultsDiv.innerHTML = ''; // Clear previous results

        const originX = parseFloat(document.getElementById('originX').value);
        const originY = parseFloat(document.getElementById('originY').value);

        for (let i = 1; i <= pointCount; i++) {
            const bearingDeg = document.getElementById(`bearingDeg${i}`).value;
            const bearingMin = document.getElementById(`bearingMin${i}`).value;
            const bearingSec = document.getElementById(`bearingSec${i}`).value;
            const distance = parseFloat(document.getElementById(`distance${i}`).value);

            const bearingRadians = dmsToRadians(bearingDeg, bearingMin, bearingSec);
            const { x, y } = calculateNewCoordinate(originX, originY, bearingRadians, distance);

            const resultItem = document.createElement('div');
            resultItem.classList.add('result-item');
            resultItem.innerHTML = `
                <h3>Point ${i} Result:</h3>
                <p><strong>Calculated X:</strong> ${x.toFixed(4)}</p>
                <p><strong>Calculated Y:</strong> ${y.toFixed(4)}</p>
            `;
            calculatedResultsDiv.appendChild(resultItem);
        }
    });
});