document.addEventListener("DOMContentLoaded", () => 
{
  const board = document.getElementById("board");
  const buttonContainer = document.getElementById("button-container");
  // Store the number of presses for each letter
  let letterPresses = {};
  // Words for the game
  const words = ["saves"];
  let currentWordIndex = 0;

  function createSquare(letter) {
    const square = document.createElement("div");
    square.classList.add("square");
    square.textContent = letter;
    board.appendChild(square);
    // Add a click event listener to each letter box
    square.addEventListener("click", () => {
      // Get the current number of presses for this letter
      const currentPresses = letterPresses[letter] || 0;
      // Determine the color based on the number of presses
      let color;
      if (currentPresses === 0) {
        color = "green";
      } else if (currentPresses === 1) {
        color = "yellow";
      } else {
        color = ""; // Empty string to remove the color
      }
      // Set the background and border color of the letter box
      square.style.backgroundColor = color;
      square.style.borderColor = color;
      // Update the number of presses for this letter
      letterPresses[letter] = (currentPresses + 1) % 3;
    });
  }

  function createWord(word) {
    for (let i = 0; i < word.length; i++) {
      createSquare(word[i]);
    }
  }

  
  function restartFlaskApp() {
    fetch('http://127.0.0.1:5000/restart', {
      method: 'POST'
    })
    .then(response => {
      if (response.ok) {
        console.log('Flask app restarted successfully!');
      } else {
        console.error('Failed to restart Flask app.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  
  function showCongratulatoryMessage() {
    alert("Congratulations!!");
  }

  function displayPredictedWord(predictedWord) {
    createWord(predictedWord);
  }

  let currentLine = 0;
  const totalLines = 8;
  const lineWordData = [];
  // Function to reset the game
  function resetGame() {
    board.innerHTML = "";
    letterPresses = {};
    currentWordIndex = 0;
    currentLine = 0;
    lineWordData.length = 0;
    words.splice(1);
    createWord(words[currentWordIndex], currentLine);
  }

  function retrieveData() {
    const wordData = {
      word: words[currentWordIndex],
      yellowLetters: [],
      greenLetters: [],
      uncoloredLetters: [],
    };

    
    const squares = document.querySelectorAll(".square");
    for (let i = currentLine * 5; i < (currentLine + 1) * 5; i++) {
      squares[i].style.pointerEvents = "none";
    }
    for (let i = currentLine * 5; i < (currentLine + 1) * 5; i++) {
      const square = squares[i]; // Corrected variable name
      const letter = square.textContent;
      const color = square.style.backgroundColor;
      if (color === "yellow") {
        wordData.yellowLetters.push({ letter, index: i % 5 }); // Corrected index
      } else if (color === "green") {
        wordData.greenLetters.push({ letter, index: i % 5 }); // Corrected index
      } else {
        wordData.uncoloredLetters.push({ letter, index: i % 5 }); // Corrected index
      }
    }
    
    console.log("Word Data:", wordData);
    
    // Add word data of the current line to the array
    lineWordData.push(wordData);

    // Lock the current line
    //const squares = document.querySelectorAll(".square");
    

    // Move to the next line
    currentLine++;

    // Check if we have displayed all the lines (up to the sixth line)
    
    fetch('http://127.0.0.1:5000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ wordData })
    })
      .then(response => response.json())
      .then(data => {
        const predictedWord = data.predictedWord;
        words.push(predictedWord);
        displayPredictedWord(predictedWord); 
        console.log("pred:",predictedWord)// Display the predicted word below the game board
      })
      .catch(error => console.error('Error:', error));
      currentWordIndex++
      if (currentLine >= totalLines) {
        // After displaying all lines, reset the game
        resetGame();
      }
    
  }

  // Display the first word
  createWord(words[currentWordIndex]);

  // Event listener for the Enter button
  const enterButton = document.querySelector('[data-key="enter"]');
  enterButton.addEventListener("click", retrieveData);

  // Event listener for the Enter key press
  document.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      retrieveData();
    }
  });

  // Handle Reset button click
  const resetButton = document.querySelector('[data-key="reset"]');
  resetButton.addEventListener("click", () => {
    restartFlaskApp(); // Restart the Flask app
    resetGame();
  });

  // Handle Thumbs Up button click
  const thumbsUpButton = document.querySelector('[data-key="thumbs-up"]');
  thumbsUpButton.addEventListener("click", () => {
    showCongratulatoryMessage();
    resetGame();
  });



});
