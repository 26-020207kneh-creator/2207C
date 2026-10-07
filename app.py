import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Mini Racing Game",
    page_icon="🏎️",
    layout="centered"
)

st.title("🏎️ Mini Racing Game")
st.caption("← → 방향키로 자동차를 움직여 장애물을 피하세요!")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
    body {
        margin: 0;
        padding: 0;
        background: #111;
        font-family: Arial, sans-serif;
        overflow: hidden;
    }

    #game {
        position: relative;
        width: 400px;
        height: 650px;
        margin: auto;
        overflow: hidden;
        background: #333;
        border: 5px solid white;
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(0,0,0,0.7);
    }

    /* 도로 */
    #road {
        position: absolute;
        width: 100%;
        height: 100%;
        background:
            linear-gradient(
                to right,
                #222 0%,
                #222 32%,
                #fff 32%,
                #fff 34%,
                #222 34%,
                #222 66%,
                #fff 66%,
                #fff 68%,
                #222 68%,
                #222 100%
            );
    }

    /* 중앙 점선 */
    .line {
        position: absolute;
        width: 8px;
        height: 70px;
        background: white;
        left: 196px;
        opacity: 0.8;
    }

    #player {
        position: absolute;
        width: 55px;
        height: 90px;
        bottom: 40px;
        left: 172px;
        background: linear-gradient(
            to right,
            #cc0000,
            #ff3333,
            #cc0000
        );
        border-radius: 12px 12px 8px 8px;
        border: 3px solid white;
        box-sizing: border-box;
        z-index: 10;
    }

    #player::before {
        content: "";
        position: absolute;
        width: 35px;
        height: 25px;
        left: 7px;
        top: 10px;
        background: #8ee7ff;
        border-radius: 6px;
        border: 2px solid #222;
    }

    #player::after {
        content: "🏎️";
        position: absolute;
        font-size: 30px;
        left: 8px;
        bottom: 8px;
    }

    .obstacle {
        position: absolute;
        width: 55px;
        height: 90px;
        background: linear-gradient(
            to right,
            #0055aa,
            #008cff,
            #0055aa
        );
        border-radius: 12px 12px 8px 8px;
        border: 3px solid white;
        box-sizing: border-box;
        z-index: 5;
    }

    .obstacle::before {
        content: "";
        position: absolute;
        width: 35px;
        height: 25px;
        left: 7px;
        top: 10px;
        background: #9eeeff;
        border-radius: 6px;
        border: 2px solid #222;
    }

    #score {
        position: absolute;
        top: 15px;
        left: 15px;
        color: white;
        font-size: 22px;
        font-weight: bold;
        z-index: 20;
        text-shadow: 2px 2px 3px black;
    }

    #speed {
        position: absolute;
        top: 45px;
        left: 15px;
        color: #ffeb3b;
        font-size: 16px;
        z-index: 20;
        text-shadow: 2px 2px 3px black;
    }

    #gameOver {
        display: none;
        position: absolute;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        color: white;
        z-index: 100;
        text-align: center;
        align-items: center;
        justify-content: center;
        flex-direction: column;
    }

    #gameOver h1 {
        color: #ff3333;
        font-size: 42px;
    }

    #gameOver button {
        padding: 12px 25px;
        font-size: 18px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        background: #ff3333;
        color: white;
    }

    #mobileControls {
        width: 400px;
        margin: 15px auto;
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }

    .control {
        flex: 1;
        padding: 15px;
        font-size: 28px;
        border: none;
        border-radius: 12px;
        background: #333;
        color: white;
        cursor: pointer;
    }

    .control:active {
        background: #ff3333;
    }

    @media (max-width: 450px) {
        #game {
            width: 95vw;
            height: 80vh;
        }

        #mobileControls {
            width: 95vw;
        }
    }
</style>
</head>

<body>

<div id="game">

    <div id="road"></div>

    <div id="score">점수: 0</div>
    <div id="speed">속도: 5</div>

    <div id="player"></div>

    <div id="gameOver">
        <h1>GAME OVER</h1>
        <p id="finalScore">점수: 0</p>
        <button onclick="restartGame()">다시 시작</button>
    </div>

</div>

<div id="mobileControls">
    <button class="control" id="leftBtn">⬅️</button>
    <button class="control" id="rightBtn">➡️</button>
</div>

<script>

const game = document.getElementById("game");
const player = document.getElementById("player");
const scoreText = document.getElementById("score");
const speedText = document.getElementById("speed");
const gameOverScreen = document.getElementById("gameOver");
const finalScore = document.getElementById("finalScore");

let playerX = 172;
let score = 0;
let speed = 5;
let gameRunning = true;

let obstacles = [];
let roadLines = [];

const playerWidth = 55;
const gameWidth = 400;


// 도로 점선 생성
for (let i = 0; i < 8; i++) {
    const line = document.createElement("div");

    line.className = "line";

    line.style.top = (i * 100 - 100) + "px";

    game.appendChild(line);

    roadLines.push(line);
}


// 장애물 생성
function createObstacle() {

    const obstacle = document.createElement("div");

    obstacle.className = "obstacle";

    const lanes = [45, 172, 300];

    const lane =
        lanes[Math.floor(Math.random() * lanes.length)];

    obstacle.style.left = lane + "px";
    obstacle.style.top = "-100px";

    game.appendChild(obstacle);

    obstacles.push({
        element: obstacle,
        x: lane,
        y: -100
    });
}


// 충돌 검사
function collision(a, b) {

    const rect1 = a.getBoundingClientRect();
    const rect2 = b.getBoundingClientRect();

    return !(
        rect1.right < rect2.left ||
        rect1.left > rect2.right ||
        rect1.bottom < rect2.top ||
        rect1.top > rect2.bottom
    );
}


// 키보드
document.addEventListener("keydown", function(event) {

    if (event.key === "ArrowLeft") {
        playerX -= 20;
    }

    if (event.key === "ArrowRight") {
        playerX += 20;
    }

    playerX =
        Math.max(
            10,
            Math.min(gameWidth - playerWidth - 10, playerX)
        );

    player.style.left = playerX + "px";
});


// 모바일 버튼
document.getElementById("leftBtn").addEventListener(
    "click",
    function() {

        playerX -= 30;

        playerX =
            Math.max(
                10,
                Math.min(gameWidth - playerWidth - 10, playerX)
            );

        player.style.left = playerX + "px";
    }
);


document.getElementById("rightBtn").addEventListener(
    "click",
    function() {

        playerX += 30;

        playerX =
            Math.max(
                10,
                Math.min(gameWidth - playerWidth - 10, playerX)
            );

        player.style.left = playerX + "px";
    }
);


// 게임 업데이트
function updateGame() {

    if (!gameRunning) {
        return;
    }

    // 점수 증가
    score++;

    scoreText.innerText =
        "점수: " + score;

    // 속도 증가
    speed =
        5 + Math.floor(score / 500);

    speedText.innerText =
        "속도: " + speed;


    // 도로 움직임
    roadLines.forEach(line => {

        let y =
            parseInt(line.style.top);

        y += speed;

        if (y > 650) {
            y = -100;
        }

        line.style.top = y + "px";
    });


    // 장애물 이동
    obstacles.forEach((obstacle, index) => {

        obstacle.y += speed;

        obstacle.element.style.top =
            obstacle.y + "px";


        // 충돌
        if (
            obstacle.y > 450 &&
            obstacle.y < 620
        ) {

            if (
                collision(
                    player,
                    obstacle.element
                )
            ) {

                endGame();

            }
        }


        // 화면 밖
        if (obstacle.y > 700) {

            obstacle.element.remove();

            obstacles.splice(index, 1);
        }

    });


    // 장애물 생성
    if (
        obstacles.length === 0 ||
        obstacles[obstacles.length - 1].y > 180
    ) {

        createObstacle();

    }

}


// 게임 종료
function endGame() {

    gameRunning = false;

    finalScore.innerText =
        "최종 점수: " + score;

    gameOverScreen.style.display =
        "flex";
}


// 다시 시작
function restartGame() {

    obstacles.forEach(
        obstacle => obstacle.element.remove()
    );

    obstacles = [];

    score = 0;
    speed = 5;

    playerX = 172;

    player.style.left =
        playerX + "px";

    gameOverScreen.style.display =
        "none";

    gameRunning = true;

}


// 게임 루프
setInterval(
    updateGame,
    30
);

</script>

</body>
</html>
"""

components.html(
    html_code,
    height=780,
    scrolling=False
)
