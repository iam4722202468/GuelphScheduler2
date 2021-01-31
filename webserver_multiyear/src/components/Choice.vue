<template>
  <div>
    <div v-if="typeof data == 'string'">
      <b-row>
        <b-col cols="10">
          <CourseSmall :code="data" :isGreen="this.parent.$parent.courses.filter(el => el.Code == data).length !== 0"/>
        </b-col>
        <b-col v-on:click="add" cols="2" class="hoverButton btn btn-outline-success" title="Add">
          <b-icon icon="plus"></b-icon>
        </b-col>
      </b-row>
    </div>
    <div v-else-if="typeof data == 'object' && data instanceof Array">
      <Choice v-for="item in data" :key="JSON.stringify(item)" :data="item" :parent="parent"/>
    </div>
    <div v-else>
      <div v-if="data['type'] == 'AND'" class="and">
        Choose All
        <Choice :data="data['groups']" :parent="parent"/>
      </div>
      <div v-else-if="data['type'] == 'CHOOSE'" class="choose">
        Choose {{ data['count'] }}
        <Choice :data="data['groups']" :parent="parent"/>
      </div>
    </div>
  </div>
</template>

<script>
import CourseSmall from '@/components/CourseSmall.vue'

export default {
  name: 'Choice',
  props: ['data', 'parent'],
  methods: {
    add: function () {
      this.parent.addCode(this.data)
    }
  },
  components: {
    CourseSmall
  }
}
</script>

<style scoped lang="scss">
.courseBox {
  margin-bottom: 10px;
  text-align: center;
}

.choose, .and {
  padding-left: 15px;
  padding-right: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
}

.hoverButton {
  border-radius: 60px;
  height: 28px;
  font-size: 0.8em;
}
</style>
