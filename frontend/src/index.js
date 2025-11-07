// src/index.js
import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import store from "./app/store";
import App from "./App";
import { markAuthChecked } from "./features/auth/authSlice"; // ✅ add this

// 🔹 Tell guards that initial auth check is done (prevents white screen/flicker)
store.dispatch(markAuthChecked());

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  // Note: StrictMode is fine; if you see double API calls in dev, you can remove it.
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);