var logged_user_id = null;
var logged_user_name = "";
var source = null;
var notification_count = 0;

function notifyUser(title, message) {
  console.log(title, message);
  $("#main-div").append(
    `<div id="dialog-${notification_count}" title="${title}" style="white-space: pre-wrap" hidden>
      <p>${message}</p>
    </div>`
  );
  $(`#dialog-${notification_count++}`).dialog({width: "40%"});
}

function joinUser() {
  logged_user_name = document.getElementById("username-input").value;
  fetch("/user", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: logged_user_name }),
  })
    .then((response) => response.json())
    .then((user) => {
      console.log(user);
      logged_user_id = user._id;
      document.getElementById("join-div").style.display = "none";
      document.getElementById("main-div").removeAttribute("hidden");
      document.getElementById(
        "profile-div"
      ).innerHTML = `<h2>Bem Vindo ${logged_user_name}</h2>`;
      source = new EventSource(`/stream?channel=user-${logged_user_id}`);

      source.addEventListener(
        "notification",
        function (event) {
          var data = JSON.parse(event.data);
          notifyUser(data.title, data.message);
        },
        false
      );

      source.addEventListener(
        "error",
        function (event) {
          console.log(event);
          notifyUser("ERRO", "Erro no servidor!");
        },
        false
      );
    });
}

function getActiveAuctions() {
  console.log("getActiveAction");
  fetch("/product", {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => {
      console.log(response);
      notifyUser("Leilões Ativos", response.length ? response : "Nenhum leilão ativo.");
    });
}

function registerProduct() {
  let price = document.getElementById("register-product-price").value;
  let name = document.getElementById("register-product-name").value;
  let date = document.getElementById("register-product-date").value;
  let desc = document.getElementById("register-product-desc").value;
  try {
    price = parseFloat(price);
  } catch (error) {
    notifyUser(data.title, `Invalid input ${error}`);
    return;
  }

  fetch("/product", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: name,
      description: desc,
      initial_price: price,
      end_date: Math.floor(new Date(date).getTime() / 1000.0),
      owner_id: logged_user_id,
    }),
  }).then((response) => response.json());
}

function bidAuction() {
  let product_id = document.getElementById("bid-auction-product-id").value;
  let value = document.getElementById("bid-auction-value").value;

  try {
    value = parseFloat(value);
  } catch (error) {
    notifyUser(data.title, `Invalid input ${error}`);
    return;
  }
  fetch("/bid", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: logged_user_id,
      product_id: product_id,
      value: value,
    }),
  }).then((response) => response.json());
}
