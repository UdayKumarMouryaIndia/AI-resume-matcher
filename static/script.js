const input = document.getElementById("resumes");
const fileCount = document.getElementById("file-count");
const fileList = document.getElementById("file-list");
const form = document.getElementById("resume-form");
const topXInput = document.getElementById("top_x");
const submitButton = document.getElementById("submit-button");

input.addEventListener("change", function () {
    fileList.replaceChildren();

    const files = Array.from(this.files);
    const pdfFiles = files.filter(file => file.name.toLowerCase().endsWith(".pdf"));

    if (files.length === 0) {
        fileCount.textContent = "No files selected";
        return;
    }

    if (files.length > 10) {
        fileCount.textContent = "Please select no more than 10 files.";
        fileCount.classList.add("error-text");
    } else if (pdfFiles.length !== files.length) {
        fileCount.textContent = "Only PDF files are allowed. Please select them again.";
        fileCount.classList.add("error-text");
    } else {
        fileCount.textContent = `✔ ${files.length} resume(s) selected`;
        fileCount.classList.remove("error-text");
    }

    files.forEach(file => {
        const li = document.createElement("li");
        const icon = document.createElement("i");
        const name = document.createElement("span");

        icon.className = "fa-solid fa-file-pdf";
        name.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;

        li.append(icon, name);
        fileList.appendChild(li);
    });
});

form.addEventListener("submit", function (event) {
    const files = Array.from(input.files);
    const allPdf = files.every(file => file.name.toLowerCase().endsWith(".pdf"));
    const topX = Number(topXInput.value);

    if (files.length === 0 || files.length > 10 || !allPdf) {
        event.preventDefault();
        alert("Please select between 1 and 10 PDF resumes.");
        return;
    }

    if (!Number.isInteger(topX) || topX < 1 || topX > 10) {
        event.preventDefault();
        alert("Top candidates must be a number between 1 and 10.");
        return;
    }

    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
});
