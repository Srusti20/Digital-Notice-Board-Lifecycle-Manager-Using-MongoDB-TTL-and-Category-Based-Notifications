importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyDGk5u59oxUqrG0ZfA2k1ONo9M_HI3wtrU",
  authDomain: "smartnoticeboard-fb51b.firebaseapp.com",
  projectId: "smartnoticeboard-fb51b",
  storageBucket: "smartnoticeboard-fb51b.firebasestorage.app",
  messagingSenderId: "1050872240810",
  appId: "1:1050872240810:web:9aeacf3e3cc5cf0c464ed3"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = { body: payload.notification.body };
  self.registration.showNotification(notificationTitle, notificationOptions);
});
