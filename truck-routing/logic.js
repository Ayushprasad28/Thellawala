submitButton = document.getElementsByTagName('button')[0];

//gets location
origin = () => {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve(pos.coords),
            (error) => reject(error.code),
            {'enableHighAccuracy': true}
        )
    }
)}


submitButton.addEventListener('click', () => {
    origin().then(resolvedValue => {
        console.log(resolvedValue)
        // let url = `http://localhost:5000?x=${resolve.latitude}&y=${resolve.longitude}`
        // console.log(JSON.stringify(resolvedValue))
        let {latitude, longitude, altitude, accuracy, altitudeAccuracy, heading, speed} = resolvedValue;
        let coords = {latitude, longitude, altitude, accuracy, altitudeAccuracy, heading, speed}
        coords = JSON.stringify(coords);
        console.log(coords)
        //promised resolved and coordinates sent to the server for placing the order
        fetch('http://localhost:5000', {method: 'post', headers:{'Content-Type': 'application/json'}, body: coords})
        .then(() => console.log('successful')).
        catch((error) => console.log(error))
    }, (error) => {
        alert(error.message)
    });
})