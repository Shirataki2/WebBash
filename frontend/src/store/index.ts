import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store<{
  isLogin: boolean;
  code: string;
  history: string[];
  username: string;
  avatarUrl: string;
}>
  ({
    state: {
      isLogin: false,
      code: "",
      history: [],
      username: "",
      avatarUrl: ""
    },
    mutations: {
      SET_LOGIN(state, isLogin: boolean) {
        state.isLogin = isLogin
      },
      SET_CODE(state, newcode: string) {
        state.code = newcode
      },
      SET_HISTORY(state, newcodes: Array<string>) {
        state.history = newcodes
      },
      SET_USERNAME(state, username: string) {
        state.username = username
      },
      SET_AVATAR_URL(state, avatarUrl: string) {
        state.avatarUrl = avatarUrl
      },
      APPEND_HISTORY(state, newcode: string) {
        state.history.push(newcode)
      },
      DELETE_FIRST_HISTORY(state) {
        state.history = state.history.slice(1)
      },
      DELETE_ALL_HISTORY(state) {
        state.history = []
      },
    },
    actions: {
      setLogin({ commit }, isLogin: boolean) {
        commit("SET_LOGIN", isLogin)
      },
      setCode({ commit }, newcode: string) {
        commit("SET_CODE", newcode)
      },
      setHistory({ commit }, newcodes: Array<string>) {
        commit("SET_HISTORY", newcodes)
      },
      setUsername({ commit }, username: string) {
        commit("SET_USERNAME", username)
      },
      setAvatarUrl({ commit }, avatarUrl: string) {
        commit("SET_AVATAR_URL", avatarUrl)
      },
      appendHistory({ commit }, newcode: string) {
        commit("APPEND_HISTORY", newcode)
      },
      deleteFirstHistory({ commit }) {
        commit("DELETE_FIRST_HISTORY");
      },
      deleteAllHistory({ commit }) {
        commit("DELETE_ALL_HISTORY");
      }
    },
    modules: {
    }
  })
