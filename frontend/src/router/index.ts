import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'
import Home from '../views/Home.vue'
import TimeLine from '../views/Timeline.vue'
import Post from '../views/Post.vue'
import User from '../views/User.vue'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/timeline',
    name: 'TimeLine',
    component: TimeLine
  },
  {
    path: '/user/:user_id/post/:post_id',
    name: 'Post',
    component: Post
  },
  {
    path: '/user/me',
    name: 'Me',
    component: User
  },
  {
    path: '/user/:user_id',
    name: 'User',
    component: User
  },
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
