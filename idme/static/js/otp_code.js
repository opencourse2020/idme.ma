    const inputs = document.getElementById("inputs");
    const inputs_elements = inputs.children;
    const otpinput = document.getElementById("id_code");
    const inputs_arr = Array.from(inputs_elements);
    var otp = otpinput.value;

inputs.addEventListener("input", function (e) {
    const target = e.target;
    const val = target.value;

    if (isNaN(val)) {
        target.value = "";
        return;
    }

    if (val != "") {
        const next = target.nextElementSibling;
        var otpcode = "";
        Array.from(inputs_elements).forEach((input) => {
        otpcode = otpcode + input.value;
            });

        otpinput.value = otpcode;
        if (next) {
            next.focus();
        }
    }
});

inputs.addEventListener("keyup", function (e) {
    const target = e.target;
    const key = e.key.toLowerCase();

    if (key == "backspace" || key == "delete") {
        target.value = "";
        var otpcode = "";
        Array.from(inputs_elements).forEach((input) => {
        otpcode = otpcode + input.value;
            });
        otpinput.value = otpcode;
        // otpinput.value = otp.substring(0, otp.length-1);
        const prev = target.previousElementSibling;
        if (prev) {
            prev.focus();
        }
        return;
    }
});


document.addEventListener('DOMContentLoaded', () => {
  //put something to paste into the console
  console.log('ABCD17');

  //handle pasting in the code
  document.addEventListener('paste', handlePaste);

  //as you type jump to the next input
  // let inputs = document.querySelectorAll('.code__input');
    let inputs = document.getElementById("inputs");
    let inputs_elements = inputs.children;
  Array.from(inputs_elements).forEach((input, index, arr) => {
    input.addEventListener('input', function (ev) {
      // arr[input]
      input.value = input.value.toUpperCase();
      arr[index + 1]?.focus();
    });
  });
});

function handlePaste(ev) {
  if (ev.target.localName !== 'input') return;
  ev.preventDefault();
  let paste = (ev.clipboardData || window.clipboardData).getData('text');
  paste = paste.toUpperCase();
  console.log(paste);
  let inputs = document.getElementById("inputs");
    let inputs_elements = inputs.children;
  // let inputs = document.querySelectorAll('.code__input');
  if (paste.length !== inputs_elements.length) return; //handle as you want
  Array.from(inputs_elements).forEach((input, index) => {
    input.focus();
    input.value = paste[index];
  });
}




