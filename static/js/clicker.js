async function incrementBlocks() {
    const response = await fetch("/mine", {method: "POST"});
        if(response.ok) {
            document.getElementById("counter").textContent = (await response.json()).blocks;
        }
}