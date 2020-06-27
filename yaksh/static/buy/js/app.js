//Variables
const courses= document.querySelector('#courses-list'),
        shoppingCartContent= document.querySelector('#cart-content tbody'),
        clearCartBtn=document.querySelector('#clear-cart');
        checkoutCartBtn=document.querySelector('#cart-checkout');





//Listeners
loadEventListeners();


function loadEventListeners(){


    courses.addEventListener('click', buycourse);

    shoppingCartContent.addEventListener('click', removeCourse);

    clearCartBtn.addEventListener('click', clearCart);

    checkoutCartBtn.addEventListener('click', checkoutCart);

    document.addEventListener('DOMContentLoaded', getFromLocalStorage);

}





//Functions

function buycourse(e){

    if(e.target.classList.contains('add-to-cart')){

    if(e.target.classList.contains('quiz-on-sale')){
        const quiz_code = e.target.parentElement.parentElement.children[0].innerText;
    const quiz_price = e.target.parentElement.parentElement.children[2].innerText;
    const quiz_id = parseInt(e.target.parentElement.parentElement.children[3].innerText);
    addIntoCart(quiz_code, quiz_price, quiz_id);
    }

    if(e.target.classList.contains('module-on-sale')){
    item_containers = e.target.parentElement.parentElement.parentElement.parentElement.children[1].firstElementChild.children
        for (var i = 0; i < item_containers.length; i++) {
            if (item_containers[i].classList.contains('card')){
                const quiz_code = item_containers[i].firstElementChild.firstElementChild.children[0].innerText;
                const quiz_price = item_containers[i].firstElementChild.firstElementChild.children[2].innerText;
                const quiz_id = parseInt(item_containers[i].firstElementChild.firstElementChild.children[3].innerText);
                addIntoCart(quiz_code, quiz_price, quiz_id);
            }
}
    }


//    getCourseInfo(course);

    }
}


function addIntoCart(quiz_code, quiz_price, quiz_id){
    const row= document.createElement('tr');
    row.innerHTML= ` 
    <tr>
    <td>
    ${quiz_code}</td>
    <td> ${quiz_price} </td>
    <td style = "display:none"> ${quiz_id} </td>
    <td> <a href ="#" class="fa fa-trash remove" data-id="${course.id}"></a> </td>


    </tr>

    `;
    shoppingCartContent.appendChild(row);

}

function removeCourse(e){

    if(e.target.classList.contains('remove')){
        

        e.target.parentElement.parentElement.remove();
    
       
    
        }
}

function clearCart(e){
    shoppingCartContent.innerHTML='';
    
}

function checkoutCart(e){
    items = e.target.parentElement.firstElementChild.tBodies[0].children;
    sum = 0
    quiz_ids = []
    for (var i = 0; i < items.length; i++) {
      sum += parseInt(items[i].cells[1].innerText.replace("Rs.", ""))
      quiz_ids.push(parseInt(items[i].cells[2].innerText))
    }
    alert(sum)
    assign_quizzes(quiz_ids)
//    window.location.href = "/letsprepare";
}

function assign_quizzes(quiz_ids) {
    submitData = {'quizzes' : quiz_ids}

    $.post("/letsprepare/assign_quizzes/",
  {
    data: JSON.stringify(submitData)
  },
  function(data, status){
    alert("\nStatus: " + status);
    window.location.href = "/letsprepare";
  });
}

function saveIntoStorage(course){

let courses= getCoursesFromStorage();

courses.push(course);

localStorage.setItem('courses', JSON.stringify(courses));
}

function getCoursesFromStorage(){
    let courses; 

    if(localStorage.getItem('courses')===null){
        courses=[];
    } else{
        course= JSON.parse(localStorage.getItem('courses'));
    
    }
    return courses;
}

function getFromLocalStorage(){
    let coursesLS= getCoursesFromStorage(); 


     coursesLS.forEach(function(course) {


        const row= document.createElement('tr');
        row.innerHTML= ` 
    <tr>
    <td>
    <img src="${course.image}" width=100>
    </td>
    <td> ${course.title} </td>
    <td> ${course.price} </td>
    <td> <a href ="#" class="remove" data-id="${course.id}">X</a> </td>


    </tr>

    `;
        shoppingCartContent.appendChild(row);
     }); 

}
