let humid_gauge; 
let temp_guage;
let thchart;
document.addEventListener('DOMContentLoaded', function() {
  //define charts
  const ctx = document.getElementById('temp_humid_chart');
  fetch('/_get_initial_data')
  .then(response => {
      if (response.ok) {
          return response.json();
      } else {
          throw new Error('Network response was not ok.');
      }
  })
  .then(data => {
    console.log(data);

    const times = data.initial_data.map(item => {
        const [day, month, year] = item.date.split('/');
        const [hour, minute, second] = item.time.split(':');
        return `${hour}:${minute}`;
    });

    const temperatures = data.initial_data.map(item => item.temperature);
    const humidities = data.initial_data.map(item => item.humidity);

    console.log("Times:", times);
    console.log("Temperatures:", temperatures);
    console.log("Humidities:", humidities);
    
    function createChart(Temperatures, humidities, Times) {
      thchart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Times,
                datasets: [
                    {
                        label: 'Temperature',
                        data: Temperatures,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Humidity',
                        data: humidities,
                        yAxisID: 'y1',
                    }
                ]
            },
            options: {
                scales: {
                    y:{
                        type: 'linear',
                        display: true,
                        position: 'left',
                    },
                    y1:{
                        type: 'linear',
                        display: true,
                        position: 'right',
                    }
                },
                maintainAspectRatio: false
            }
        });
    }

    createChart(temperatures, humidities, times); 

  })
  .catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
  });

  humid_gauge = new JustGage({
    id: "humid-guage",
    title: "Humidity",
    label: "%",
    value: 0,
    min: 0,
    max: 100,
    decimals: 2,
    pointer: true,
    gaugeWidthScale: 0.6,
    customSectors: {
      ranges: [{
        color : "#e00000",
        lo : 0,
        hi : 60
      },{
        color : "#ff8400",
        lo : 61,
        hi : 74
      },{
        color : "#c0ffe0",
        lo : 75,
        hi : 95
      },{
        color : "#ff8400",
        lo : 96,
        hi : 100
      }
    ]
    }
  });
  temp_guage = new JustGage({
    id: "temp-guage",
    title: "Temperature",
    label: "°C",
    value: 0,
    pointer: true,
    min: 0,
    max: 30,
    decimals: 2,
    gaugeWidthScale: 0.6
  });
  $.getJSON('/_get_data', function(data) {
    if (data.error) {
      console.error(data.error);
    } else {

      // //gauges 
      humid_gauge.refresh(data.humidity);
      temp_guage.refresh(data.temperature);   


      //leds
      update_led_state(data.box_fan_state, 'box_fan_led');    
      update_led_state(data.mister_state, 'mister_led');       
      update_led_state(data.inline_fan_state, 'inline_fan_led'); 
      update_led_state(data.pump_state, 'pump_led'); 



      function update_led_state(state, ledId) {
        const led_element = document.getElementById(ledId);
        if (led_element) {
          if (state === 'On') {
            led_element.classList.add('green'); 
            led_element.classList.remove('red');
          } else if (state === 'Off') {
            led_element.classList.add('red');
            led_element.classList.remove('green');
          } else {
            console.error(`Invalid state: ${state}`);
          }
        } else {
          console.error(`LED element not found: ${ledId}`);
        }
      }

    }
  });
  fetch('/_get_image') 
    .then(response => response.blob())
    .then(blob => {
      const imageUrl = URL.createObjectURL(blob);
      document.getElementById('webcamImage').src = imageUrl;
    })
    .catch(error => console.error('Error fetching image:', error));
});

$(document).ready(function() { 
  
    setInterval(function() {
      $.getJSON('/_get_data', function(data) {
        if (data.error) {
          console.error(data.error);
        } else {

          //gauges 
          humid_gauge.refresh(data.humidity);
          temp_guage.refresh(data.temperature);

          //leds
          update_led_state(data.box_fan_state, 'box_fan_led');    
          update_led_state(data.mister_state, 'mister_led');       
          update_led_state(data.inline_fan_state, 'inline_fan_led'); 
          update_led_state(data.pump_state, 'pump_led'); 

          if (thchart) {
            const timeLabel = data.time.substring(0, 5);

            thchart.data.labels.push(timeLabel);
            thchart.data.datasets[0].data.push(data.temperature);
            thchart.data.datasets[1].data.push(data.humidity);
  
            // if (thchart.data.labels.length > 20) {
            //   thchart.data.labels.shift();
            //   thchart.data.datasets[0].data.shift();
            //   thchart.data.datasets[1].data.shift();
            // }
  
            thchart.update();
          }


          function update_led_state(state, ledId) {
            const led_element = document.getElementById(ledId);
            if (led_element) {
              if (state === 'On') {
                led_element.classList.add('green'); 
                led_element.classList.remove('red');
              } else if (state === 'Off') {
                led_element.classList.add('red');
                led_element.classList.remove('green');
              } else {
                console.error(`Invalid state: ${state}`);
              }
            } else {
              console.error(`LED element not found: ${ledId}`);
            }
          }

        }
      });
      fetch('/_get_image') 
      .then(response => response.blob())
      .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById('webcamImage').src = imageUrl;
      })
      .catch(error => console.error('Error fetching image:', error));
    }, 
    90000);
  });


