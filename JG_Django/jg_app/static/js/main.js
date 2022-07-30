
var done = ['Tang', 'Ning', 'Coco', 'Peter', 'Paul'];
// new
var imgList=['images/person1.png','images/person2.png','images/person3.png','images/person4.png','images/person5.png']

// var done = [];

const appendItem = (textContent,imgContent, parentNodeId) => {
    const newItem = document.createElement('li');
    newItem.classList.add('todo_item');
    // new
    const img = document.createElement('img');
    img.src=imgContent
    img.width=100
    // newItemImg.innerHTML = `<p class='todo_content'>${imgContent}</p>`
    newItem.innerHTML = `<p class='todo_content'>${textContent}</p>`
    // new
    newItem.appendChild(img)



    document.querySelector(`#${parentNodeId}`).appendChild(newItem);

    // document.querySelector(`#${parentNodeId}`).appendChild(img);
};


const itemMove = (event, newParentNodeId) => {
    const target = event.target;
    console.log(target.parentNode.childNodes)
    if (target.classList.contains('todo_content')) {
        // done.unshift(target.textContent);
        // todo = todo.filter(value => value !== target.textContent);

        // new
        const newItem = document.createElement('li');
        newItem.classList.add('todo_item');
        newItem.innerHTML = `<p class='todo_content'>${target.textContent}</p>`
        console.log(newItem)
        newItem.appendChild(target.parentNode.childNodes[1])
        document.querySelector(`#${newParentNodeId}`).appendChild(newItem);
        target.parentNode.remove();

        // appendItem(target.textContent,target.imgContent, newParentNodeId);

    }
}

// render all todo items
for (var i = 0; i < done.length; i++) {
    appendItem(done[i],imgList[i], 'done');
}

// add event listener to parent node todo, then see whether the clicked element contains todo_content class
document.querySelector('#todo').addEventListener('click', function (event) {
    itemMove(event, 'done');
});

document.querySelector('#done').addEventListener('click', function(event) {
    itemMove(event, 'todo');
});
