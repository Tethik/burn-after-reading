<template>
  <div class="about">
    <div id="paper">
      <h2 id="title">Paper</h2>
      <p>Paper is a digital asset that can be used to represent various types of information.</p>
      <p>It can be used to create and manage digital assets, such as documents, images, and videos.</p>
      <p>Paper can also be used to create and manage digital identities, such as user profiles and social media
        accounts.</p>
      <button @click="startFire">Start Fire</button>
    </div>    
    <canvas id="fire-canvas" width="0" height="0"></canvas>    
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }

  #fire-canvas{
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1;
    pointer-events: none;
  }

  #paper {
    margin: 0 auto;
    width: 1000px;
    padding: 20px;
    height: 800px;
    /* background-color: #f9f9f9; */
    /* border-radius: 8px; */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    /* background:     
      linear-gradient(black 0 0)bottom left/ 100% 98%,   
      linear-gradient(red 0 0)bottom left/ 100% 99%,
      linear-gradient(orange 0 0)bottom left/ 100% 100%,
      #ccc; */
    background-position-y: -4500%;
    background-repeat: no-repeat;
  }

  #paper {
    /* animation: expand-fire 10s forwards; */
  }

  @keyframes expand-fire {
    0% {
      color: pink;
      background-position-y: 180%;
    }
    20% {
      color: red;
      background-position-y: 60%;
    }
    40% {
      color: yellow;
      background-position-y: 40%;
    }
    60% {
      color: orange;
      background-position-y: 20%;
    }
    80% {
      background-position-y: 20%;
      color: white;    
    }
    100% {
      background-position-y: 0%;
      color: blue;  
    }
  }
}
</style>

<script setup>
function startFire() {
  const canvas = document.getElementById('fire-canvas');
  const paper = document.getElementById('paper');

  // Set the canvas size
  const size = paper.getBoundingClientRect();
  canvas.setAttribute('width', size.width);
  canvas.setAttribute('height', size.height);
  canvas.style.position = 'absolute';
  canvas.style.top = paper.offsetTop + 'px';
  canvas.style.left = paper.offsetLeft + 'px';
  canvas.style.zIndex = '1';

  const ctx = canvas.getContext('2d');
  
  const gridSize = 13; // size of each pixel in the grid
  const evolveRate = 0.23; // rate at which the fire evolves
  const pixels = []; // the burn values for each pixel
  const gridWidth = Math.ceil(canvas.width / gridSize);
  const gridHeight = Math.ceil(canvas.height / gridSize);

  const colorProgression = [
    // 'rgba(92, 51, 44, 1)', // smolder - brown
    // 'brown',    
    'rgba(255, 0, 0, 1)', // burning - red
    'rgba(255, 67, 0, 1)', // glowing - orange
    'rgba(255, 165, 0, 1)', // hot - yellow          
  ].reverse(); // ash = -2, -1 = not burning


  // const colorProgression = [
  //   // 'rgba(92, 51, 44, 1)', // smolder - brown
  //   'brown',
  //   '#3f3f74',
  //   '#306082',
  //   '#5b6ee1',
  // ]; // ash = -2, -1 = not burning
  
  
  // Initialize the pixels array with -1 (not burning)
  for (let y = 0; y < gridHeight; y++) {
    const row = [];
    for (let x = 0; x < gridWidth; x++) {

      // Draw a grid of squares (for debugging)
      // ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
      // ctx.strokeStyle = 'rgba(0, 0, 0, 0.5)';
      // ctx.strokeRect(x*gridSize, y*gridSize, gridSize, gridSize);      

      row.push(-1);
    }
    pixels.push(row);
  }

  // Draw the fire effect
  function drawFire(updatedPixels) {
    for (let {x, y, pixel} of updatedPixels) {                      
        if (pixel === -2) {          
          ctx.clearRect(x * gridSize, y * gridSize, gridSize, gridSize);
          ctx.fillStyle = 'rgba(0, 0, 0, 0.80)';
        } else if (pixel === -1) {
          ctx.clearRect(x * gridSize, y * gridSize, gridSize, gridSize);          
        } else {
          ctx.fillStyle = colorProgression[pixel];
        }

        ctx.fillRect(x * gridSize, y * gridSize, gridSize, gridSize);
    }    
  }

  function gp(y, x) {
    if (pixels[y] === undefined) {
      return -2;
    }
    if (pixels[y][x] === undefined) {
      return -2;
    }
    return pixels[y][x];
  }
 

  function tick() {
    // IDEA: use copy of pixels to avoid modifying the original array while iterating?
    // IDEA: be smarter about which pixels to update - no need to scan the whole grid

    // Update the burn values for each pixel
    const updatedPixels = [];
    
    let s = 0;
    for (let y = 0; y < gridHeight; y++) {
      for (let x = 0; x < gridWidth; x++) {
        const pixel = pixels[y][x];
        s += pixel;

        if (pixel === -2) { // ash
          continue;
        }
        
        if (Math.random() > evolveRate) {    
          continue;
        }
        

        // Are any of the surrounding pixels burning?
        const nearbyFire = 
            gp(y - 1, x) > -1 || // above
            gp(y + 1, x) > -1 || // below
            gp(y, x - 1) > -1 || // left
            gp(y, x + 1) > -1; // right

        const nearbyFuel = 
            gp(y - 1, x) === -1 || // above
            gp(y + 1, x) === -1 || // below
            gp(y, x - 1) === -1 || // left
            gp(y, x + 1) === -1; // right
        
        if (pixel === -1 && nearbyFire) { // not burning -> brown                               
          updatedPixels.push({x, y, pixel: 0});          
        } else if (pixel > -1 && pixel < colorProgression.length - 1) {            
          updatedPixels.push({x, y, pixel: pixels[y][x] + 1});          
        } else if (pixel === colorProgression.length - 1 && !nearbyFuel) {
          // burning -> ash                    
          updatedPixels.push({x, y, pixel: -2});
        }         
      }
    }

    // Update pixels
    updatedPixels.forEach(({x, y, pixel}) => {
      pixels[y][x] = pixel;
    });

    drawFire(updatedPixels);
    if (s !== -2 * gridWidth * gridHeight) { 
      requestAnimationFrame(tick); // AnimationFrame happens at 60fps
    } else {
      console.log("fire done");      
    }    
  }  

  // Kindle the fire
  const startPixels = [
    // {x: 0, y: 0, pixel: 0}, 
    {x: gridWidth-1, y: gridHeight - 1, pixel: 0}
  ];
  for (let {x, y, pixel} of startPixels) {
    pixels[y][x] = pixel; 
  }  
  drawFire(startPixels);

  // Start the animation loop
  tick();
}

</script>
