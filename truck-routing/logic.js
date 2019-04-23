// setInterval(() => console.log(document.getElementById('address').value), 3000);

let submitButtonHere = document.getElementById('here');
let submitButtonElsewhere = document.getElementById('at-an-address');

//gets location
let origin = () => {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve(pos.coords),
            (error) => reject(error.code),
            {'enableHighAccuracy': true}
        );
    }
    );};

submitButtonHere.addEventListener('click', () => {
    origin().then(resolvedValue => {
        console.log(resolvedValue);
        // let url = `http://localhost:5000?x=${resolve.latitude}&y=${resolve.longitude}`
        // console.log(JSON.stringify(resolvedValue))
        let {latitude, longitude, altitude, accuracy, altitudeAccuracy, heading, speed} = resolvedValue;
        let coords = {latitude, longitude, altitude, accuracy, altitudeAccuracy, heading, speed};
        coords = JSON.stringify(coords);
        console.log(coords);
        //promised resolved and coordinates sent to the server for placing the order
        fetch('http://localhost:5000', {method: 'post', headers:{'Content-Type': 'application/json'}, body: coords})
            .then(() => console.log('successful')).
            catch((error) => console.log(error));
    }, (error) => {
        alert(error.message);
    });
});

submitButtonElsewhere.addEventListener('click', () => {
    let addressString = document.getElementById('address').value; 
    fetch('http://localhost:5000', {method: 'post', headers:{'Content-Type': 'application/x-www-form-urlencoded'}, body: addressString})
        .then(() => console.log('order placed elsewhere successfully')).
        catch((error) => console.log(error));
}, (error) => {
    alert(error.message);
    
});