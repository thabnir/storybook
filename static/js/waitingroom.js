const checkStatus = async () => {
  let response = await fetch("/api/waitingroom");
  if (response.status == 200) {
    window.location.href = "/game";
  } else {
    setTimeout(() => {
      checkStatus();
    }, 1000);
  }
}

checkStatus();
