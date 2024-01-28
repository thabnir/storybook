const actionForm = document.getElementById("action-form");

actionForm.addEventListener("submit", e => {
  e.preventDefault();

  const formData = new FormData();
  formData.append("action", document.getElementById("action").value);
  document.getElementById("action").value = "";
  fetch("/api/action", {
    method: "POST",
    body: formData,
  }).then(e => e.text()).then(e => {
    if (e.text) {
      alert(e.text);
    }
  });
});

const pollMessages = (msg_id) => {
  fetch("/api/getmessages").then((e) => e.json()).then((e) => {
    for (; msg_id < e.length; msg_id++) {
      const timeline = document.getElementById("story");
      
      const cardDiv = document.createElement("div");
      cardDiv.className = 'card mb-3 w-50 mx-auto';

      const imgElement = document.createElement('img');
      imgElement.src = `data:image/jpeg;base64,${e[msg_id]["base64_image"]}`;
      imgElement.className = 'card-img-top p-3';
      imgElement.style.borderRadius = '1.5rem';

      const cardBodyDiv = document.createElement('div');
      cardBodyDiv.className = 'card-body';

      const cardTitle = document.createElement('h5');
      cardTitle.className = 'card-title';
      cardTitle.textContent = e[msg_id]["name"];

      const cardText = document.createElement('p');
      cardText.className = 'card-text';
      cardText.textContent = e[msg_id]["content"];

      cardBodyDiv.appendChild(cardTitle);
      cardBodyDiv.appendChild(cardText);
    
      if (e[msg_id]["base64_image"]) {
        cardDiv.appendChild(imgElement);
      }
      cardDiv.appendChild(cardBodyDiv);

      timeline.appendChild(cardDiv);
    }
    setTimeout(() => {
      pollMessages(msg_id);
    }, 1000);
  });
}

pollMessages(0);

const pollHealth = () => {
  fetch("/api/gethealth").then((e) => e.json()).then((e) => {
    console.log(e);

    document.getElementById("progress-div-1").ariaValueNow = `${e[0]}`;
    document.getElementById("progress-bar-div-1").style.width = `${e[0]}%`;
    document.getElementById("progress-bar-div-1").innerHTML = `${e[0]}%`;

    document.getElementById("progress-div-2").ariaValueNow = `${e[0]}`;
    document.getElementById("progress-bar-div-2").style.width = `${e[0]}%`;
    document.getElementById("progress-bar-div-2").innerHTML = `${e[0]}%`;

    setTimeout(() => {
      pollHealth();
    }, 1000);
  });
}

pollHealth();
