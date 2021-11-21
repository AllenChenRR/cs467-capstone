animal_type_select = document.getElementById('animal_type');
breed_select = document.getElementById('breed');


animal_type_select.onchange = function () {
    animal_type = animal_type_select.value;
    console.log(window.location.origin + '/type/' + animal_type)
    fetch(window.location.origin + '/type/' + animal_type)
        .then(function (response) {
            response.json().then(data => {
                optionHTML = '';
                for (let i = 0; i < data.length; i++) {
                    value = data[i][0];
                    label = data[i][1];
                    optionHTML += '<option value="' + value + '">' + label + '</option>';
                };
                breed_select.innerHTML = optionHTML;
            });
        })
        .catch(error => {
            console.log(error);
        });
}