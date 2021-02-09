function ASSERT(condition, message) {
  const udef = undefined;
  if (condition == false) {
    console.log(`!!!! ASSERTION FAILED: ${message} !!!!`);
    udef(42); // some code that is guaranteed to fail
  }
}

function tryGetCookie(key) {
  if (typeof Storage !== undefined) {
    const value = localStorage.getItem(key);
    return [value === null ? false : true, value];
  } else {
    return [false, null];
  }
}

function trySetCookie(key, value) {
  if (typeof Storage !== undefined) {
    localStorage.setItem(key, value);
    return [true, value];
  } else {
    return [false, null];
  }
}

// constants
const LOGIN_STATE_COOKIE = 'loggedIn'; // possible value: 'true' or 'false'

const LOGIN_MODAL_LINK = 'loginModalLink';
const LOGIN_MODAL = 'loginModal';
const LOGOUT_MODAL_LINK = 'logoutModalLink';
const LOGOUT_MODAL = 'logoutModal';

const LOGIN_SUBMIT_LINK = 'loginSubmitLink';
const LOGOUT_SUBMIT_LINK = 'logoutSubmitLink';

// entrypoint
document.addEventListener('DOMContentLoaded', function(e) {
  // init logic
  function refreshLoginStateView() {
    const cookieKey = LOGIN_STATE_COOKIE;
    let [readLoginState, loginState] = tryGetCookie(cookieKey);
    console.log(`Read login state cookie: ${cookieKey}=${loginState}`);

    const loginModalLink = document.getElementById(LOGIN_MODAL_LINK);
    const logoutModalLink = document.getElementById(LOGOUT_MODAL_LINK);

    if (loginState === 'true') {
      loginModalLink.style.display = 'none';
      logoutModalLink.style.display = 'inline-block';
    } else {
      loginModalLink.style.display = 'inline-block';
      logoutModalLink.style.display = 'none';
    }
  }

  refreshLoginStateView();

  // modal logic
  let currentModal = null;
  const CURRENT_MODAL_INACTIVE = null;

  function setupModal(modalId, modalLinkId) {
    const modal = document.getElementById(modalId);
    ASSERT(modal !== null, `No modal with id ${modalId}`);

    const modalLink = document.getElementById(modalLinkId);
    ASSERT(modalLink !== null, `No modal link with id ${modalLinkId}`);

    modalLink.onclick = function(e) {
      if (currentModal === CURRENT_MODAL_INACTIVE) {
        currentModal = modal;
        currentModal.style.display = 'block';
      }
    };
  }

  window.addEventListener('click', function(e) {
    if (e.target === currentModal) {
      currentModal.style.display = 'none';
      currentModal = CURRENT_MODAL_INACTIVE;
    }
  });

  setupModal(LOGIN_MODAL, LOGIN_MODAL_LINK);
  setupModal(LOGOUT_MODAL, LOGOUT_MODAL_LINK);

  // login / logout logic
  const loginSubmitLink = document.getElementById(LOGIN_SUBMIT_LINK);
  ASSERT(loginSubmitLink !== null, `No login link with id ${LOGIN_SUBMIT_LINK}`);

  loginSubmitLink.onclick = function(e) {
    const cookieKey = LOGIN_STATE_COOKIE;
    let [didWrite, writtenValue] = trySetCookie(cookieKey, 'true');
    ASSERT(didWrite && writtenValue === 'true', `Could not set cookie`);
    console.log(`Wrote cookie: ${cookieKey}=${writtenValue}`);

    // TODO update state
    refreshLoginStateView();
  };

  const logoutSubmitLink = document.getElementById(LOGOUT_SUBMIT_LINK);
  ASSERT(logoutSubmitLink !== null, `No logout link with id ${LOGOUT_SUBMIT_LINK}`);

  logoutSubmitLink.onclick = function(e) {
    const cookieKey = LOGIN_STATE_COOKIE;
    let [didWrite, writtenValue] = trySetCookie(cookieKey, 'false');
    ASSERT(didWrite && writtenValue === 'false', `Could not set cookie`);
    console.log(`Wrote cookie: ${cookieKey}=${writtenValue}`);

    // TODO update state
    refreshLoginStateView();
  };
});
