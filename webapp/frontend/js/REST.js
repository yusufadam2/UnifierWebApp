// Performs a REST API call.
// @param url The url to which to make a request
// @param method The HTTP method to use for the request (i.e. GET, POST)
// @param isAsync Whether the request should be asynchronous (99% of the time, this should be true)
// @param timeoutMs Time to wait before terminating the request (0 means no timeout)
// @param headers An array of header key-value pairs to include with the request
// @param body The data to send in the body of the request
// @param onsuccess Callback function with signature 'function(xhr, xhrResponse, xhrResponseType) { }'
// @param onfailure Callback function with signature 'function(xhr, xhrStatus) { }'
// @param onprogress Callback function with signature 'function(xhr, currentBytes, totalBytes, isTotalKnown) { }'
// @param ontimeout Callback function with signature 'function(xhr, timeoutMs) { }'
function REST(url, method, isAsync, timeoutMs,
              headers, body,
              onsuccess = null,
              onfailure = null,
              onprogress = null,
              ontimeout = null) {
  const xhr = new XMLHttpRequest();
  xhr.open(method, url, isAsync);
  xhr.timeout = timeoutMs;

  // settings headers
  headers.forEach(function(pair) {
    const [header, value] = pair;
    xhr.setRequestHeader(header, value);
  });

  // tracking request
  xhr.upload.onload = function() {
    if (xhr.status !== 0 && xhr.status !== 200) {
      console.log(`[${method}:${url}] Unsucessful body upload: ${xhr.status}`);
    }
  };

  xhr.upload.onprogress = function(e) {
    console.log(`[${method}:${url}] Upload: ${e.loaded}/${e.total} (known total length? ${e.lengthComputable})`);
  };

  xhr.upload.onerror = function() {
    console.log(`[${method}:${url}] Network error prevented sending body!`);
  };

  // tracking response
  xhr.onload = function() {
    if (xhr.status === 200) {
      onsuccess && onsuccess(xhr, xhr.response, xhr.responseType);
    } else {
      onfailure && onfailure(xhr, xhr.status);
    }
  };

  xhr.onprogress = function(e) {
    console.log(`[${method}:${url}] Download: ${e.loaded}/${e.total} (known total length? ${e.lengthComputable})`);
    onprogress && onprogress(xhr, e.loaded, e.total, e.lengthComputable);
  };

  xhr.ontimeout = function(e) {
    console.log(`[${method}:${url}] Request timed out!`);
    ontimeout && ontimeout(xhr, timeoutMs);
  };

  xhr.onerror = function() {
    console.log(`[${method}:${url}] Network error prevented fetching response!`);
  };

  // performs the request
  xhr.send(body);
}
