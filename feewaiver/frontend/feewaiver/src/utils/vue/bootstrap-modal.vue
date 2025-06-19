<template>
    <Transition :name="transition">
        <div v-show="show">
            <div class="modal" @click.self="clickMask">
                <div class="modal-dialog modal-dialog-centered" :class="modalClass" role="document">
                    <div class="modal-content">
                        <!--Header-->
                        <slot name="header">
                            <div class="modal-header">
                                <h5 class="modal-title">{{title}}</h5>
                                <button type="button" class="btn-close" @click="cancel" aria-label="Close"></button>
                            </div>
                        </slot>
                        <!--Container-->
                        <div class="modal-body">
                            <slot></slot>
                        </div>
                        <!--Footer-->
                        <div class="modal-footer">
                            <slot name="footer">
                                <button id="okBtn" type="button" :class="okClass" @click="ok">{{okText}}</button>
                                <button type="button" :class="cancelClass" @click="cancel">{{cancelText}}</button>
                            </slot>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show"></div>
        </div>
    </Transition>
</template>

<script>
    /**
     * Bootstrap Style Modal Component for Vue
     * Depend on Bootstrap.css
     */

     export default {
        props: {
            title: {
                type: String,
                default: 'Modal'
            },
            small: {
                type: Boolean,
                default: false
            },
            large: {
                type: Boolean,
                default: false
            },
            xlarge: {
                type: Boolean,
                default: false
            },
            full: {
                type: Boolean,
                default: false
            },
            force: {
                type: Boolean,
                default: false
            },
            transition: {
                type: String,
                default: 'modal'
            },
            okText: {
                type: String,
                default: 'OK'
            },
            cancelText: {
                type: String,
                default: 'Cancel'
            },
            okClass: {
                type: String,
                default: 'btn btn-primary'
            },
            cancelClass: {
                type: String,
                default: 'btn btn-secondary'
            },
            closeWhenOK: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                duration: null
            };
        },
        computed: {
            modalClass () {
                return {
                    'modal-xl': this.xlarge,
                    'modal-lg': this.large,
                    'modal-sm': this.small,
                    'modal-full': this.full
                }
            },
            show: function() {
                return this.$parent.isModalOpen;
            }
        },
        mounted () {
            if (this.show) {
                document.body.className += ' modal-open';
            }
        },
        beforeUnmount () {
            document.body.className = document.body.className.replace(/\s?modal-open/, '');
        },
        emits: [ 'ok', 'cancel' ],
        watch: {
            show (value) {
                if (value) {
                    document.body.className += ' modal-open';
                }
                else {

                    window.setTimeout(() => {
                        document.body.className = document.body.className.replace(/\s?modal-open/, '');
                    }, this.duration || 0);
                }
            }
        },
        methods: {
            ok () {
                this.$emit('ok');
                if (this.closeWhenOK) {
                    this.show = false;
                }
            },
            cancel () {
                this.$emit('cancel');
                this.$parent.close();
            },
            clickMask () {
                if (!this.force) {
                    this.cancel();
                }
            },
        }
     };
</script>


<style scoped>
    .modal {
        display: block;
    }
    .modal .btn {
        margin-bottom: 0px;
    }
    .modal-header {
        border-top-left-radius: .3rem;
        border-top-right-radius: .3rem;
    }
    .modal-footer{
        border-bottom-left-radius: .3rem;
        border-bottom-right-radius: .3rem;
    }
    .modal-body, .modal-footer, .modal-header {
        /*background-color: #F5F5F5;
        color: #333333;*/
        background-color: #efefef;
        color: #333333;
    }
    .modal-transition {
        transition: all .6s ease;
    }
    .modal-leave {
        border-radius: 1px !important;
    }
    .modal-transition .modal-dialog, .modal-transition .modal-backdrop {
        transition: all .5s ease;
    }
    .modal-enter .modal-dialog, .modal-leave .modal-dialog {
        opacity: 0;
        transform: translateY(-30%);
    }
    .modal-enter .modal-backdrop, .modal-leave .modal-backdrop {
        opacity: 0;
    }
    .btn-close {
        opacity: .3;
    }
    .close:hover {
        opacity: .7;
    }
    #okBtn {
        margin-bottom: 0px;
    }
</style>
