function loadItemsFromJSON(jsonFile, listId){
    fetch(`json/${jsonFile}`)
    .then(res => res.json())
    .then(data => {
        const lista = document.getElementById(listId);
        lista.innerHTML = '';
        Object.keys(data).forEach(key => {
            const item = data[key];
            const li = document.createElement('li');

            const img = document.createElement('img');
            img.src = item.image;

            const details = document.createElement('div');
            details.className = 'item-details';

            const name = document.createElement('div');
            name.className = 'item-name';
            name.textContent = item.name;

            const price = document.createElement('div');
            price.className = 'item-price';
            price.textContent = `Precio: ${item.price}`;

            const desc = document.createElement('div');
            desc.className = 'item-description';
            desc.textContent = item.description;

            const btn = document.createElement('button');
            btn.textContent = "Contactar WhatsApp";
            btn.onclick = () => window.open(`https://wa.me/34611844783?text=Hola,+estoy+interesado+en+${encodeURIComponent(item.reference)}`, '_blank');

            details.appendChild(name);
            details.appendChild(price);
            details.appendChild(desc);
            details.appendChild(btn);

            li.appendChild(img);
            li.appendChild(details);
            lista.appendChild(li);
        });
    }).catch(err => console.warn('No se pudieron cargar los items desde:', jsonFile, err));
}

// Llamadas para cargar las listas
loadItemsFromJSON('products.json', 'productos-list');
loadItemsFromJSON('offers.json', 'ofertas-list');
loadItemsFromJSON('novelties.json', 'novedades-list');
