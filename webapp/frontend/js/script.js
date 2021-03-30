function hasCookie(key) {
  return document.cookie.split(';').some(function(arg) {
    return arg.trim().indexOf(`${key}=`) === 0;
  });
}

// constants
const SESSION_COOKIE = 'unifier-session';
const LOGIN_NAV_LINK_ID = 'loginNavLink';
const LOGOUT_NAV_LINK_ID = 'logoutNavLink';
const DASHBOARD_NAV_LINK_ID = 'dashboardNavLink';

// entrypoint
document.addEventListener('DOMContentLoaded', function(e) {
  const hasSessionCookie = hasCookie(SESSION_COOKIE);

  const loginNavLink = document.getElementById(LOGIN_NAV_LINK_ID);
  const logoutNavLink = document.getElementById(LOGOUT_NAV_LINK_ID);
  const dashboardNavLink = document.getElementById(DASHBOARD_NAV_LINK_ID);

  if (hasSessionCookie) {
    loginNavLink.style.display = 'none';
    logoutNavLink.style.display = 'inline-block';
    dashboardNavLink.style.display = 'inline-block';
  } else {
    loginNavLink.style.display = 'inline-block';
    logoutNavLink.style.display = 'none';
    dashboardNavLink.style.display = 'none';
 }
});

