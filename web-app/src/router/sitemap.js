function getRoutesList(routes, pre) {
    return routes.reduce((array, route) => {
        const path = `${pre}${route.path}`;

        if (route.path !== '*') {
        array.push(path);
        }

        if (route.children) {
        array.push(...getRoutesList(route.children, `${path}/`));
        }

        return array;
    }, []);
}

function getRoutesXML(router) {
    const list = getRoutesList(router.options.routes, 'https://smart-api.info')
        .map(route => {
        let r = route.includes(':component?') ? route.replace(':component?', 'KP') : route
        return `<url><loc>${r}</loc></url>`
        })
        .join('\r\n');
    return `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
        ${list}
    </urlset>`;
}

export default getRoutesXML