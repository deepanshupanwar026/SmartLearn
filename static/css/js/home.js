const words = [
  "Get You Hired",
  "Build Your Career",
  "Earn Certificates",
  "Level Up Fast"
];

let index = 0;
let charIndex = 0;
const typingElement = document.querySelector(".typing-text");

function typeWord() {
  if (charIndex < words[index].length) {
    typingElement.textContent += words[index][charIndex];
    charIndex++;
    setTimeout(typeWord, 100);
  } else {
    setTimeout(eraseWord, 2000);
  }
}

function eraseWord() {
  if (charIndex > 0) {
    typingElement.textContent =
      words[index].substring(0, charIndex - 1);
    charIndex--;
    setTimeout(eraseWord, 60);
  } else {
    index = (index + 1) % words.length;
    setTimeout(typeWord, 400);
  }
}

document.addEventListener("DOMContentLoaded", typeWord);

// COUNT UP ANIMATION
document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".trust-number");

  counters.forEach(counter => {
    const target = parseFloat(counter.dataset.count);
    let count = 0;
    const increment = target / 80;

    const updateCount = () => {
      count += increment;
      if (count < target) {
        counter.textContent = target % 1 === 0
          ? Math.floor(count)
          : count.toFixed(1);
        requestAnimationFrame(updateCount);
      } else {
        counter.textContent = target;
      }
    };

    updateCount();
  });
});


  document.addEventListener("DOMContentLoaded", function () {
    const counters = document.querySelectorAll(".trust-number");

    counters.forEach(counter => {
      const target = parseFloat(counter.dataset.target);
      const suffix = counter.dataset.suffix || "";
      const isDecimal = target % 1 !== 0;

      let current = 0;
      const duration = 1500; // total animation time (ms)
      const frameRate = 30;
      const totalFrames = duration / frameRate;
      const increment = target / totalFrames;

      const updateCounter = () => {
        current += increment;

        if (current < target) {
          counter.innerText = isDecimal
            ? current.toFixed(1) + suffix
            : Math.floor(current) + suffix;
          setTimeout(updateCounter, frameRate);
        } else {
          counter.innerText = target + suffix;
        }
      };

      updateCounter();
    });
  });
  

