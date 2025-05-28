document.getElementById("getWeatherBtn").addEventListener("click", () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const accuracy = position.coords.accuracy;

        console.log("위도:", lat);
        console.log("경도:", lon);
        console.log("정확도:", accuracy, "미터");

        // 정확도 검사
        if (accuracy > 5000) {
          document.getElementById("weatherResult").textContent = 
            "정확한 위치를 가져오지 못했습니다 (정확도: " + accuracy + "m)";
          return;
        }

        try {
          const response = await fetch("/weather", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ latitude: lat, longitude: lon }),
          });

          if (!response.ok) {
            throw new Error("서버 응답 오류");
          }

          const data = await response.json();
          document.getElementById("weatherResult").textContent = JSON.stringify(data, null, 2);
        } catch (err) {
          document.getElementById("weatherResult").textContent = "에러 발생: " + err.message;
        }
      },
      (error) => {
        alert("위치 정보를 가져올 수 없습니다: " + error.message);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  } else {
    alert("이 브라우저는 위치 정보를 지원하지 않습니다.");
  }
});
