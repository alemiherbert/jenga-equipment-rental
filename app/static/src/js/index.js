import './site-navigation';
import './theme-switcher';
import './theme-detection';
import './featured-equipment';
import './register';
import './login';
import './check-auth'
import './fetch-interceptor';
import './display-equipment';
import './range-group';
import './cart';
import './checkout';
import './dash-equipment';
import './add-equipment';
import './edit-equipment';
import carousel from './carousel';
import featuredEquipment from './featured-equipment';
import equipmentGrid from './equipment-grid';
import Alpine from 'alpinejs';
import focus from '@alpinejs/focus';
import feather from 'feather-icons'

// import searchComponent from './components/search';
feather.replace();

window.Alpine = Alpine;
// window.searchComponent = searchComponent;
Alpine.plugin(focus)
Alpine.data('carousel', carousel);
Alpine.data('featuredEquipment', featuredEquipment);
Alpine.data('equipmentGrid', equipmentGrid);
Alpine.start();
