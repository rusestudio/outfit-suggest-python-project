document.getElementById("getWeatherBtn").addEventListener("click", () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

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
      }
    );
  } else {
    alert("이 브라우저는 위치 정보를 지원하지 않습니다.");
  }
});
