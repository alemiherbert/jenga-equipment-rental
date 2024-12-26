import './site-navigation';
import './theme-switcher';
import './theme-detection';
import './featured-equipment';
import './register';
import './login';
import './check-auth'
import './fetch-interceptor';
import carousel from './carousel';
import featuredEquipment from './featured-equipment';
import equipmentGrid from './equipment-grid';
import Alpine from 'alpinejs';
import focus from '@alpinejs/focus'
// import searchComponent from './components/search';

window.Alpine = Alpine;
// window.searchComponent = searchComponent;
Alpine.plugin(focus)
Alpine.data('carousel', carousel);
Alpine.data('featuredEquipment', featuredEquipment);
Alpine.data('equipmentGrid', equipmentGrid);
Alpine.start();
